# 📦 Sistema Integrado de Compras: MRP de Alumínio + Forecast Cambial (SARIMA)

![CI Pipeline](https://github.com/SEU_USUARIO/aluminio_stremilit/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.13-blue.svg)
![Framework](https://img.shields.io/badge/framework-Streamlit-red.svg)
![Tests](https://img.shields.io/badge/tests-7%20passed-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Aplicação online

 [Acesse o dashboard no Streamlit Cloud](https://aluminiostremilit-hruay2ejxasaykwvihembm.streamlit.app/)

**Tópicos:** `python` · `streamlit` · `supply-chain` · `mrp` · `forecasting` · `sarima` · `machine-learning`

Sistema analítico e motor de decisão desenvolvido para **Planejamento e Controle de Produção (PCP)** e **Suprimentos Estratégicos**. Integra a lógica clássica de ressuprimento industrial (MRP) a modelos de previsão de séries temporais (SARIMA) e APIs do mercado financeiro, mitigando riscos de ruptura de estoque e exposição à volatilidade cambial.

---

## 🎯 Objetivo de Negócio

A compra de matérias-primas importadas ou atreladas a commodities (como o alumínio na LME) envolve dois vetores críticos de risco:
1. **Risco Operacional de Ruptura:** Paradas de linha provocadas por consumo acima do previsto ou atrasos no *Lead Time*.
2. **Risco de Mercado (Câmbio):** Flutuações na taxa de câmbio USD/BRL que impactam diretamente o custo unitário da tonelada em Reais (BRL).

Este projeto automatiza a identificação do momento ótimo de emissão de pedidos de compra (*Purchase Orders - PO*), respeitando restrições contratuais de fornecimento (*MOQ*) e fornecendo sensibilidade financeira futura via projeção probabilística do dólar.

---

## 🏗️ Arquitetura do Projeto

O código adota o princípio de separação de responsabilidades (*Clean Architecture* aplicada a dashboards analíticos):

```text
aluminio_stremilit/
│
├── app.py                  # Orquestrador da aplicação Streamlit
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação técnica do repositório
│
├── src/
│   ├── __init__.py
│   ├── config.py           # Centralização de parâmetros mestres e constantes
│   ├── data_sources.py     # Conexão resiliente a APIs externas (BCB/SGS e Yahoo Finance)
│   ├── mrp.py              # Regras de negócio puras (ROP, Cobertura, PO e MOQ)
│   ├── forecasting.py      # Modelagem estatística SARIMA e intervalos de confiança
│   └── ui_components.py    # Renderização de KPIs, alertas e gráficos interativos
│
└── tests/
    └── test_mrp.py         # Testes unitários com pytest para validação de regras de PCP