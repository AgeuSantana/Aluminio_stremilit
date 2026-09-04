"""
Suíte de testes unitários para a camada de regras de negócio (src/mrp.py).
"""

import pytest
from src.mrp import (
    calcular_rop,
    calcular_cobertura,
    converter_preco_brl,
    avaliar_decisao_compra,
)


def test_calcular_rop_sucesso():
    # Consumo: 5 ton/dia, Lead Time: 15 dias, Estoque de Segurança: 50 ton
    # ROP esperado = 50 + (5 * 15) = 125 ton
    rop = calcular_rop(consumo_diario=5.0, lead_time=15, estoque_seguranca=50.0)
    assert rop == 125.0


def test_calcular_rop_valores_negativos():
    # Deve levantar ValueError caso algum parâmetro operacional seja negativo
    with pytest.raises(ValueError):
        calcular_rop(consumo_diario=-5.0, lead_time=15, estoque_seguranca=50.0)


def test_calcular_cobertura_padrao():
    # Estoque atual: 80 ton, Consumo: 5 ton/dia -> 16 dias de cobertura
    dias = calcular_cobertura(estoque_atual=80.0, consumo_diario=5.0)
    assert dias == 16.0


def test_calcular_cobertura_consumo_zero():
    # Fábrica parada não consome: deve retornar inf sem gerar ZeroDivisionError
    dias = calcular_cobertura(estoque_atual=80.0, consumo_diario=0.0)
    assert dias == float("inf")


def test_converter_preco_brl():
    # 2.500 USD/ton a um câmbio de R$ 5,20 = R$ 13.000,00/ton
    preco_brl = converter_preco_brl(preco_usd=2500.0, cambio_usd_brl=5.20)
    assert preco_brl == 13000.0


def test_avaliar_decisao_compra_status_estavel():
    # Estoque atual (150 ton) maior que ROP (125 ton)
    resultado = avaliar_decisao_compra(
        estoque_atual=150.0,
        rop=125.0,
        moq=30.0,
        preco_ton_brl=12000.0
    )
    assert resultado["status"] == "ESTAVEL"
    assert resultado["alerta"] is False
    assert resultado["volume_sugerido_ton"] == 0.0
    assert resultado["custo_estimado_brl"] == 0.0


def test_avaliar_decisao_compra_emergencial_com_moq():
    # Estoque atual (80 ton) <= ROP (125 ton) -> Déficit de 45 ton
    # MOQ = 30 ton -> Próximo múltiplo para cobrir o déficit (45 ton) é 60 ton (2 x 30)
    resultado = avaliar_decisao_compra(
        estoque_atual=80.0,
        rop=125.0,
        moq=30.0,
        preco_ton_brl=10000.0
    )
    assert resultado["status"] == "COMPRA_EMERGENCIAL"
    assert resultado["alerta"] is True
    assert resultado["volume_sugerido_ton"] == 60.0
    assert resultado["custo_estimado_brl"] == 600000.0