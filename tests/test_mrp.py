"""
Suíte de testes unitários para o motor de MRP (src/mrp.py).
"""

import pytest
from src.mrp import (
    calcular_rop,
    calcular_cobertura,
    converter_preco_brl,
    calcular_custo_aquisicao_nacional,
    avaliar_decisao_compra,
)


def test_calcular_rop_sucesso():
    # ROP = 50 + (5 * 15) = 125 ton
    assert calcular_rop(5.0, 15, 50.0) == 125.0


def test_calcular_rop_valores_negativos():
    with pytest.raises(ValueError):
        calcular_rop(-5.0, 15, 50.0)


def test_calcular_cobertura_padrao():
    assert calcular_cobertura(80.0, 5.0) == 16.0


def test_calcular_cobertura_consumo_zero():
    assert calcular_cobertura(80.0, 0.0) == float("inf")


def test_converter_preco_brl():
    assert converter_preco_brl(2500.0, 5.20) == 13000.0


def test_calcular_custo_aquisicao_nacional():
    # LME: 2400 USD + Premio: 100 USD = 2500 USD
    # Cambio: 5.0 -> Metal: 12.500 BRL
    # Frete: 300 BRL + Seguro (1% de 12.500): 125 BRL -> Total: 12.925 BRL/ton
    resultado = calcular_custo_aquisicao_nacional(
        preco_lme_usd=2400.0,
        cambio_usd_brl=5.0,
        premio_produtor_usd=100.0,
        frete_rodoviario_brl=300.0,
        seguro_carga_pct=1.0
    )
    assert resultado["faturado_usd"] == 2500.0
    assert resultado["metal_brl"] == 12500.0
    assert resultado["custo_total_brl_ton"] == 12925.0


def test_avaliar_decisao_compra_estavel():
    resultado = avaliar_decisao_compra(150.0, 125.0, 30.0, 12000.0)
    assert resultado["status"] == "ESTAVEL"
    assert resultado["alerta"] is False
    assert resultado["volume_sugerido_ton"] == 0.0


def test_avaliar_decisao_compra_emergencial_com_moq():
    # Estoque 80 vs ROP 125 -> Déficit de 45 ton -> 2 lotes de MOQ (30) = 60 ton
    resultado = avaliar_decisao_compra(80.0, 125.0, 30.0, 10000.0)
    assert resultado["status"] == "COMPRA_EMERGENCIAL"
    assert resultado["alerta"] is True
    assert resultado["volume_sugerido_ton"] == 60.0
    assert resultado["custo_estimado_brl"] == 600000.0