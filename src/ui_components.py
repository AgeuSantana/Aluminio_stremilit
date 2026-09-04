"""
Componentes de interface visual (UI) para o Streamlit.

Centraliza a renderização de KPIs operacionais, alertas do motor de decisão
e visualizações gráficas de séries temporais.
"""

from typing import Dict, Any
import pandas as pd
import streamlit as st


def renderizar_kpis(
    lme_usd_ton: float,
    usd_brl: float,
    cobertura_dias: float,
    rop: float
) -> None:
    """Renderiza a faixa de cards principais de métricas do sistema."""
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric(
        label="Alumínio LME",
        value=f"${lme_usd_ton:,.2f}",
        help="Cotação spot ou contrato futuro representativo"
    )
    col2.metric(
        label="Câmbio USD/BRL",
        value=f"R$ {usd_brl:.4f}",
        help="Taxa PTAX coletada via Banco Central do Brasil"
    )
    col3.metric(
        label="Autonomia de Estoque",
        value=f"{cobertura_dias:.1f} Dias",
        help="Dias de operação suportados pelo saldo físico atual"
    )
    col4.metric(
        label="Ponto de Pedido (ROP)",
        value=f"{rop:.1f} ton",
        help="Gatilho de ressuprimento: Estoque Segurança + (Consumo * Lead Time)"
    )
    st.divider()


def renderizar_alerta_decisao(decisao: Dict[str, Any], estoque_atual: float, rop: float) -> None:
    """Exibe o parecer do motor de decisão de compras com base no ROP e MOQ."""
    st.subheader("Parecer Técnico do MRP")
    
    if decisao["alerta"]:
        st.error("🚨 **RECOMENDAÇÃO: COMPRA EMERGENCIAL NECESSÁRIA!**")
        st.write(decisao["mensagem"])
    else:
        st.success("✅ **STATUS OPERACIONAL ESTÁVEL: Sem risco iminente de ruptura.**")
        st.write(
            f"O estoque atual ({estoque_atual:.1f}t) está acima do Ponto de Pedido ({rop:.1f}t). "
            "Recomenda-se manter a programação padrão de fábrica."
        )
    st.divider()


def renderizar_grafico_forecast(
    df_historico: pd.DataFrame,
    df_forecast: pd.DataFrame,
    janela_historica_dias: int = 60
) -> None:
    """
    Consolida o histórico recente e a projeção SARIMA em um único gráfico.
    """
    st.subheader("Projeção de Câmbio USD/BRL (SARIMA 30 Dias)")
    
    # Recorta apenas o período recente para melhor visualização
    corte_historico = df_historico.tail(janela_historica_dias).copy()
    
    # Monta estrutura combinada para renderização
    df_plot = pd.DataFrame(index=corte_historico.index.union(df_forecast.index))
    df_plot["Histórico Real"] = corte_historico["usd_brl"]
    df_plot["Previsão (SARIMA)"] = df_forecast["yhat"]
    df_plot["Limite Superior (IC)"] = df_forecast["limite_superior"]
    df_plot["Limite Inferior (IC)"] = df_forecast["limite_inferior"]
    
    # Conecta visualmente o último ponto histórico à projeção
    ultimo_ponto_data = corte_historico.index[-1]
    ultimo_ponto_valor = corte_historico["usd_brl"].iloc[-1]
    df_plot.loc[ultimo_ponto_data, "Previsão (SARIMA)"] = ultimo_ponto_valor
    df_plot.loc[ultimo_ponto_data, "Limite Superior (IC)"] = ultimo_ponto_valor
    df_plot.loc[ultimo_ponto_data, "Limite Inferior (IC)"] = ultimo_ponto_valor

    st.line_chart(df_plot)
    st.caption("Linhas de Limite indicam o intervalo de confiança projetado pelo modelo.")