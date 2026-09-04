"""
Camada de integração com fontes externas de dados (APIs financeiras).

Coleta cotações de câmbio (USD/BRL) via API do Banco Central do Brasil (SGS)
e preços de commodities via yfinance, com tratamento de exceções e fallback.
"""

from typing import Tuple, Optional
import requests
import pandas as pd
import yfinance as yf

from src.config import (
    BCB_SGS_URL,
    YFINANCE_ALUMINIO_TICKER,
    DIAS_HISTORICO_CAMBIO,
    DEFAULT_ALUMINIO_MANUAL
)


def obter_historico_cambio(n_dias: int = DIAS_HISTORICO_CAMBIO) -> pd.DataFrame:
    """
    Obtém série histórica diária de taxa de câmbio USD/BRL do SGS/BCB.
    
    Retorna DataFrame com índice em Datetime e coluna 'usd_brl'.
    """
    url = BCB_SGS_URL.format(n_dias=n_dias)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        dados = response.json()

        df = pd.DataFrame(dados)
        df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df = df.rename(columns={"valor": "usd_brl"}).set_index("data")
        df = df.sort_index()
        
        # Preenchimento de eventuais dias sem cotação (fins de semana/feriados)
        df = df.ffill().bfill()
        return df

    except Exception as erro:
        # Em caso de falha de conexão, retorna DataFrame sintético para não travar o fluxo
        print(f"[AVISO] Falha ao coletar dados do BCB: {erro}. Utilizando fallback.")
        datas = pd.date_range(end=pd.Timestamp.today(), periods=30, freq="B")
        return pd.DataFrame({"usd_brl": [5.20] * len(datas)}, index=datas)


def obter_cambio_atual() -> float:
    """Retorna o valor spot mais recente do USD/BRL."""
    df = obter_historico_cambio(n_dias=10)
    if not df.empty and "usd_brl" in df.columns:
        return float(df["usd_brl"].iloc[-1])
    return 5.20


def obter_cotacao_aluminio(ticker: str = YFINANCE_ALUMINIO_TICKER) -> Tuple[float, str]:
    """
    Obtém o preço de fechamento mais recente da tonelada de alumínio via Yahoo Finance.
    
    Retorna:
        Tuple[float, str]: (preco_usd_ton, fonte_ou_status)
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period="5d")
        
        if not hist.empty and "Close" in hist.columns:
            preco_recente = float(hist["Close"].dropna().iloc[-1])
            if preco_recente > 0:
                return round(preco_recente, 2), "Yahoo Finance (LME Proxy)"
                
        # Se vier vazio ou zerado, aciona contingência
        return DEFAULT_ALUMINIO_MANUAL, "Fallback (Manual Padrão)"
        
    except Exception as erro:
        print(f"[AVISO] Falha ao consultar Yahoo Finance ({ticker}): {erro}. Usando valor padrão.")
        return DEFAULT_ALUMINIO_MANUAL, "Fallback (Erro de Conexão)"