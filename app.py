"""
Ponto de entrada (Entrypoint) da aplicação Streamlit.

Orquestra os módulos de configuração, coleta de dados, regras de MRP,
previsão SARIMA e renderização da interface gráfica.
"""
from src.ui_components import (
    aplicar_estilo_css_customizado,
    renderizar_kpis,
    renderizar_alerta_decisao,
    renderizar_grafico_forecast,
)
import streamlit as st

from src.config import (
    PAGE_TITLE,
    PAGE_ICON,
    DEFAULT_LEAD_TIME,
    DEFAULT_ESTOQUE_SEGURANCA,
    DEFAULT_MOQ,
    DEFAULT_CONSUMO_DIARIO,
    DEFAULT_ESTOQUE_ATUAL,
    CACHE_TTL_SEGUNDOS,
)
from src.data_sources import (
    obter_historico_cambio,
    obter_cotacao_aluminio,
)
from src.mrp import (
    calcular_rop,
    calcular_cobertura,
    converter_preco_brl,
    avaliar_decisao_compra,
)
from src.forecasting import projetar_cenarios_cambio
from src.ui_components import (
    renderizar_kpis,
    renderizar_alerta_decisao,
    renderizar_grafico_forecast,
)

# 1. Configuração inicial da página
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)
# Aplicação do tema dark e componentes customizados
aplicar_estilo_css_customizado()

st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption("Painel Integrado de Suprimentos: Planejamento de Necessidades de Materiais & Gestão de Risco Cambial")

# 2. Funções de carregamento com Cache (evita chamadas redundantes a APIs externas)
@st.cache_data(ttl=CACHE_TTL_SEGUNDOS)
def carregar_dados_mercado():
    df_cambio = obter_historico_cambio()
    preco_aluminio, fonte_aluminio = obter_cotacao_aluminio()
    return df_cambio, preco_aluminio, fonte_aluminio


@st.cache_data(ttl=CACHE_TTL_SEGUNDOS)
def carregar_projecao_cambio(df_cambio):
    return projetar_cenarios_cambio(df_cambio)


# Coleta de dados externos
with st.spinner("Conectando às fontes de dados (Banco Central do Brasil / LME)..."):
    df_cambio, preco_aluminio_usd, fonte_aluminio = carregar_dados_mercado()
    cambio_atual = float(df_cambio["usd_brl"].iloc[-1])
    df_forecast, cambio_projetado = carregar_projecao_cambio(df_cambio)

# 3. Barra Lateral (Parâmetros Operacionais e Sensibilidade)
st.sidebar.header("⚙️ Parâmetros Operacionais (PCP)")

lead_time = st.sidebar.number_input(
    "Lead Time de Fornecimento (dias)",
    min_value=1,
    value=int(DEFAULT_LEAD_TIME),
    step=1
)
estoque_seg = st.sidebar.number_input(
    "Estoque de Segurança (ton)",
    min_value=0.0,
    value=float(DEFAULT_ESTOQUE_SEGURANCA),
    step=5.0
)
moq = st.sidebar.number_input(
    "Lote Mínimo de Compra - MOQ (ton)",
    min_value=1.0,
    value=float(DEFAULT_MOQ),
    step=5.0
)
consumo_diario = st.sidebar.number_input(
    "Taxa de Consumo Diário (ton)",
    min_value=0.1,
    value=float(DEFAULT_CONSUMO_DIARIO),
    step=0.5
)
estoque_atual = st.sidebar.number_input(
    "Saldo Físico Atual em Estoque (ton)",
    min_value=0.0,
    value=float(DEFAULT_ESTOQUE_ATUAL),
    step=5.0
)

st.sidebar.divider()
st.sidebar.caption(f"Fonte do Alumínio: **{fonte_aluminio}**")
st.sidebar.caption(f"Última cotação USD: **R$ {cambio_atual:.4f}**")

# 4. Motor de Cálculo de MRP
rop = calcular_rop(consumo_diario, lead_time, estoque_seg)
cobertura_dias = calcular_cobertura(estoque_atual, consumo_diario)
preco_aluminio_brl = converter_preco_brl(preco_aluminio_usd, cambio_atual)
decisao = avaliar_decisao_compra(estoque_atual, rop, moq, preco_aluminio_brl)

# 5. Renderização da Interface
# Bloco de Métricas Chave
renderizar_kpis(
    lme_usd_ton=preco_aluminio_usd,
    usd_brl=cambio_atual,
    cobertura_dias=cobertura_dias,
    rop=rop
)

# Bloco de Parecer Operacional / Decisão de PO
renderizar_alerta_decisao(
    decisao=decisao,
    estoque_atual=estoque_atual,
    rop=rop
)

# Bloco de Séries Temporais / Projeção SARIMA
renderizar_grafico_forecast(
    df_historico=df_cambio,
    df_forecast=df_forecast
)

# Análise de Sensibilidade Financeira do Forecast
variacao_cambio_pct = ((cambio_projetado - cambio_atual) / cambio_atual) * 100
st.info(
    f"💡 **Sensibilidade Cambial (30 dias):** O modelo SARIMA projeta o dólar em "
    f"**R$ {cambio_projetado:.4f}** (variação estimada de **{variacao_cambio_pct:+.2f}%**). "
    f"O custo projetado da tonelada de alumínio em 30 dias é de aproximadamente "
    f"**R$ {preco_aluminio_usd * cambio_projetado:,.2f}**."
)