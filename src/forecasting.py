"""
Módulo de previsão de séries temporais (Forecasting).

Implementa modelo SARIMA para prever a tendência da taxa de câmbio USD/BRL
e fornecer intervalos de confiança para tomadas de decisão sob risco.
"""

from typing import Dict, Any, Tuple
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from src.config import SARIMA_ORDER, DIAS_FORECAST, IC_ALPHA


def treinar_modelo_sarima(df_historico: pd.DataFrame, coluna_alvo: str = "usd_brl") -> Any:
    """
    Treina o modelo SARIMA com base no histórico fornecido.
    
    Retorna o objeto de resultados do statsmodels se bem sucedido,
    ou None caso a massa de dados seja insuficiente.
    """
    if df_historico.empty or len(df_historico) < 30:
        return None

    try:
        # A supressão de warnings no fit é ideal para ambientes de produção/dashboards
        modelo = SARIMAX(
            df_historico[coluna_alvo],
            order=SARIMA_ORDER,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        resultados = modelo.fit(disp=False)
        return resultados
    except Exception as erro:
        print(f"[AVISO] Falha no treinamento do modelo SARIMA: {erro}")
        return None


def projetar_cenarios_cambio(
    df_historico: pd.DataFrame,
    dias_previsao: int = DIAS_FORECAST
) -> Tuple[pd.DataFrame, float]:
    """
    Gera a projeção futura com intervalos de confiança.
    
    Retorna:
        Tuple contendo:
        - DataFrame com as datas futuras, valores previstos (yhat) e limites (inferior e superior).
        - O valor médio projetado para o final do período (horizonte_final).
    """
    resultados = treinar_modelo_sarima(df_historico)
    
    ultima_data = df_historico.index[-1]
    # Cria os dias futuros usando calendário de dias úteis ('B' = Business days)
    datas_futuras = pd.date_range(start=ultima_data, periods=dias_previsao + 1, freq="B")[1:]
    
    if resultados is None:
        # Fallback de segurança: projeção "flat" baseada no último valor conhecido
        ultimo_valor = float(df_historico["usd_brl"].iloc[-1])
        df_forecast = pd.DataFrame({
            "data": datas_futuras,
            "yhat": [ultimo_valor] * dias_previsao,
            "limite_inferior": [ultimo_valor * 0.98] * dias_previsao,
            "limite_superior": [ultimo_valor * 1.02] * dias_previsao
        }).set_index("data")
        return df_forecast, ultimo_valor

    try:
        # Obtém previsão e intervalos de confiança
        previsao = resultados.get_forecast(steps=dias_previsao)
        intervalos = previsao.conf_int(alpha=IC_ALPHA)
        
        df_forecast = pd.DataFrame({
            "data": datas_futuras,
            "yhat": previsao.predicted_mean.values,
            "limite_inferior": intervalos.iloc[:, 0].values,
            "limite_superior": intervalos.iloc[:, 1].values
        }).set_index("data")
        
        projetado_final = float(df_forecast["yhat"].iloc[-1])
        return df_forecast, projetado_final

    except Exception as erro:
        # Fallback de segurança na geração da projeção
        print(f"[AVISO] Erro ao gerar steps de forecast: {erro}")
        ultimo_valor = float(df_historico["usd_brl"].iloc[-1])
        df_forecast = pd.DataFrame({
            "data": datas_futuras,
            "yhat": [ultimo_valor] * dias_previsao,
            "limite_inferior": [ultimo_valor] * dias_previsao,
            "limite_superior": [ultimo_valor] * dias_previsao
        }).set_index("data")
        return df_forecast, ultimo_valor