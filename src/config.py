"""
Configurações e constantes do projeto.

Centraliza parâmetros da interface, fontes de dados, modelo SARIMA,
parâmetros mestres de PCP e formação de custo no mercado nacional.
"""

# ============================================================
# FONTES DE DADOS
# ============================================================
BCB_SGS_URL = (
    "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/"
    "dados/ultimos/{n_dias}?formato=json"
)

# Proxy para preço do alumínio (futuro LME na CME via Yahoo Finance)
YFINANCE_ALUMINIO_TICKER = "ALI=F"

# ============================================================
# FORECASTING
# ============================================================
DIAS_HISTORICO_CAMBIO = 500
DIAS_FORECAST = 30
CACHE_TTL_SEGUNDOS = 3600
SARIMA_ORDER = (1, 1, 1)
IC_ALPHA = 0.20  # 80% de intervalo de confiança

# ============================================================
# PARÂMETROS PADRÃO DO MRP (Valores Mestres de PCP)
# ============================================================
DEFAULT_LEAD_TIME = 15
DEFAULT_ESTOQUE_SEGURANCA = 50.0
DEFAULT_MOQ = 30.0
DEFAULT_CONSUMO_DIARIO = 5.0
DEFAULT_ESTOQUE_ATUAL = 80.0
DEFAULT_ALUMINIO_MANUAL = 2450.0  # USD/ton caso a API oscile

# ============================================================
# PARÂMETROS DE COMPRA NACIONAL (MERCADO INTERNO)
# ============================================================
DEFAULT_PREMIO_PRODUTOR_USD = 120.0   # USD/ton (prêmio de liga/lingote sobre LME)
DEFAULT_FRETE_RODOVIARIO_BRL = 280.0  # R$/ton (frete rodoviário até fábrica)
DEFAULT_SEGURO_CARGA_PCT = 0.15       # 0.15% seguro de transporte rodoviário

# ============================================================
# CONFIGURAÇÕES DA INTERFACE
# ============================================================
PAGE_TITLE = "Compra de Alumínio — MRP + Câmbio"
PAGE_ICON = "📦"