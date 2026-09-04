"""
Motor de cálculo de MRP (Material Requirements Planning) para compra de alumínio.

Contém funções determinísticas para cálculo de ponto de pedido, autonomia,
conversão financeira e recomendação de emissão de Purchase Order (PO).
"""

from typing import Dict, Any


def calcular_rop(consumo_diario: float, lead_time: int, estoque_seguranca: float) -> float:
    """
    Calcula o Ponto de Pedido (Reorder Point - ROP).
    
    Fórmula: ROP = Estoque de Segurança + (Consumo Diário * Lead Time)
    """
    if consumo_diario < 0 or lead_time < 0 or estoque_seguranca < 0:
        raise ValueError("Parâmetros operacionais não podem ser negativos.")
    return estoque_seguranca + (consumo_diario * lead_time)


def calcular_cobertura(estoque_atual: float, consumo_diario: float) -> float:
    """
    Calcula a autonomia do estoque em dias.
    Retorna infinito caso o consumo diário seja zero para evitar ZeroDivisionError.
    """
    if consumo_diario <= 0:
        return float("inf")
    return estoque_atual / consumo_diario


def converter_preco_brl(preco_usd: float, cambio_usd_brl: float) -> float:
    """Calcula o valor unitário da tonelada em Reais (BRL)."""
    return preco_usd * cambio_usd_brl


def avaliar_decisao_compra(
    estoque_atual: float,
    rop: float,
    moq: float,
    preco_ton_brl: float
) -> Dict[str, Any]:
    """
    Avalia a condição de ruptura e gera o parecer técnico de ressuprimento.

    Retorna um dicionário estruturado com o status operacional, quantidade sugerida
    e impacto financeiro estimado.
    """
    precisa_comprar = estoque_atual <= rop

    if precisa_comprar:
        # Sugestão básica: repor pelo menos o Lote Mínimo (MOQ)
        # ou o déficit necessário para retornar ao patamar seguro
        deficit = rop - estoque_atual
        volume_sugerido = max(moq, deficit)
        
        # Ajuste para múltiplo do MOQ se necessário
        if volume_sugerido % moq != 0:
            volume_sugerido = ((volume_sugerido // moq) + 1) * moq

        custo_estimado = volume_sugerido * preco_ton_brl

        return {
            "status": "COMPRA_EMERGENCIAL",
            "alerta": True,
            "volume_sugerido_ton": volume_sugerido,
            "custo_estimado_brl": custo_estimado,
            "mensagem": (
                f"Estoque físico ({estoque_atual:.1f}t) atingiu ou rompeu o ROP ({rop:.1f}t). "
                f"Emitir PO emergencial de no mínimo {volume_sugerido:.1f} toneladas "
                f"(estimado em R$ {custo_estimado:,.2f})."
            )
        }

    return {
        "status": "ESTAVEL",
        "alerta": False,
        "volume_sugerido_ton": 0.0,
        "custo_estimado_brl": 0.0,
        "mensagem": "Níveis de estoque acima do Ponto de Pedido. Sem necessidade de PO imediato."
    }