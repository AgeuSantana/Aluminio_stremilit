"""
Motor de cálculo de MRP (Material Requirements Planning) para compra de alumínio.

Contém funções determinísticas para cálculo de ponto de pedido, autonomia,
formação de preço de compra no mercado nacional e recomendação de emissão de PO.
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
    Calcula a autonomia do estoque físico em dias.
    Retorna infinito se consumo_diario <= 0 para evitar divisão por zero.
    """
    if consumo_diario <= 0:
        return float("inf")
    return estoque_atual / consumo_diario


def converter_preco_brl(preco_usd: float, cambio_usd_brl: float) -> float:
    """Calcula o valor unitário da tonelada em Reais (BRL)."""
    return preco_usd * cambio_usd_brl


def calcular_custo_aquisicao_nacional(
    preco_lme_usd: float,
    cambio_usd_brl: float,
    premio_produtor_usd: float,
    frete_rodoviario_brl: float,
    seguro_carga_pct: float
) -> Dict[str, float]:
    """
    Calcula o custo efetivo de aquisição de alumínio no mercado interno.

    Estrutura:
    1. Preço Faturado Metal (USD) = LME + Prêmio de Produtor
    2. Custo do Metal (BRL) = Preço Faturado Metal * Câmbio
    3. Seguro Rodoviário (BRL) = Custo do Metal * (seguro_carga_pct / 100)
    4. Custo Total em Fábrica (BRL/ton) = Custo do Metal + Frete Rodoviário + Seguro
    """
    preco_faturado_usd = preco_lme_usd + premio_produtor_usd
    custo_metal_brl = preco_faturado_usd * cambio_usd_brl
    seguro_brl = custo_metal_brl * (seguro_carga_pct / 100.0)
    custo_total_fabrica_brl = custo_metal_brl + frete_rodoviario_brl + seguro_brl

    return {
        "lme_usd": round(preco_lme_usd, 2),
        "premio_usd": round(premio_produtor_usd, 2),
        "faturado_usd": round(preco_faturado_usd, 2),
        "metal_brl": round(custo_metal_brl, 2),
        "frete_brl": round(frete_rodoviario_brl, 2),
        "seguro_brl": round(seguro_brl, 2),
        "custo_total_brl_ton": round(custo_total_fabrica_brl, 2)
    }


def avaliar_decisao_compra(
    estoque_atual: float,
    rop: float,
    moq: float,
    preco_ton_brl: float
) -> Dict[str, Any]:
    """
    Avalia a condição de estoque contra o ROP e emite parecer técnico de PO.

    Se estoque_atual <= rop, calcula o volume sugerido cobrindo o déficit
    e respeitando o Lote Mínimo de Compra (MOQ) em múltiplos inteiros.
    """
    precisa_comprar = estoque_atual <= rop

    if precisa_comprar:
        deficit = rop - estoque_atual
        volume_sugerido = max(moq, deficit)

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