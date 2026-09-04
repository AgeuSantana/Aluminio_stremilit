"""
Componentes de interface visual (UI) para o Streamlit.

Design System moderno: Dark Mode com detalhes em Cinza Profundo e Azul Celeste Neon.
Utiliza Plotly para gráficos analíticos de séries temporais.
"""

from typing import Dict, Any
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def aplicar_estilo_css_customizado() -> None:
    """Injeta CSS customizado para acabamento glassmorphism e cores personalizadas."""
    st.markdown(
        """
        <style>
        /* Fundo principal e tipografia */
        .stApp {
            background: linear-gradient(135deg, #0b0f19 0%, #0f172a 100%);
            color: #f1f5f9;
        }

        /* Sidebar com cinza profundo e borda sutil */
        section[data-testid="stSidebar"] {
            background-color: #0d1322 !important;
            border-right: 1px solid rgba(56, 189, 248, 0.15);
        }

        /* Cartões de Métricas customizados */
        div[data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 16px 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #38bdf8;
        }

        div[data-testid="stMetricLabel"] {
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        div[data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 1.6rem !important;
            font-weight: 700;
            text-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
        }

        /* Caixas de Alerta Estilizadas */
        .alerta-emergencial {
            background: linear-gradient(90deg, rgba(239, 68, 68, 0.15) 0%, rgba(17, 24, 39, 0.9) 100%);
            border-left: 4px solid #ef4444;
            border-radius: 8px;
            padding: 18px 24px;
            margin: 15px 0;
            border-top: 1px solid rgba(239, 68, 68, 0.2);
            border-right: 1px solid rgba(239, 68, 68, 0.2);
            border-bottom: 1px solid rgba(239, 68, 68, 0.2);
        }

        .alerta-estavel {
            background: linear-gradient(90deg, rgba(14, 165, 233, 0.15) 0%, rgba(17, 24, 39, 0.9) 100%);
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            padding: 18px 24px;
            margin: 15px 0;
            border-top: 1px solid rgba(56, 189, 248, 0.2);
            border-right: 1px solid rgba(56, 189, 248, 0.2);
            border-bottom: 1px solid rgba(56, 189, 248, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def renderizar_kpis(
    lme_usd_ton: float,
    usd_brl: float,
    cobertura_dias: float,
    rop: float
) -> None:
    """Renderiza a faixa superior de métricas com design em cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Alumínio LME", f"${lme_usd_ton:,.2f}")
    col2.metric("Câmbio USD/BRL", f"R$ {usd_brl:.4f}")
    col3.metric("Autonomia de Estoque", f"{cobertura_dias:.1f} Dias")
    col4.metric("Ponto de Pedido (ROP)", f"{rop:.1f} ton")
    st.write("")


def renderizar_alerta_decisao(decisao: Dict[str, Any], estoque_atual: float, rop: float) -> None:
    """Exibe parecer técnico moderno e contrastante para compras."""
    st.markdown("### 📋 Parecer Técnico de Ressuprimento (PCP)")
    
    if decisao["alerta"]:
        st.markdown(
            f"""
            <div class="alerta-emergencial">
                <h4 style="color: #f87171; margin: 0 0 8px 0;">🚨 GATILHO DE REABASTECIMENTO ACIONADO</h4>
                <p style="margin: 0; color: #cbd5e1;">{decisao["mensagem"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div class="alerta-estavel">
                <h4 style="color: #38bdf8; margin: 0 0 8px 0;">✅ FLUXO OPERACIONAL ESTÁVEL</h4>
                <p style="margin: 0; color: #cbd5e1;">
                    O estoque físico atual (<b>{estoque_atual:.1f}t</b>) está acima do ROP de segurança (<b>{rop:.1f}t</b>). 
                    Nenhuma ordem emergencial necessária no momento.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


def renderizar_grafico_forecast(
    df_historico: pd.DataFrame,
    df_forecast: pd.DataFrame,
    janela_historica_dias: int = 60
) -> None:
    """Gera gráfico escuro e interativo em Plotly com destaque em Azul Celeste."""
    st.markdown("### 📈 Projeção Cambial USD/BRL — Modelo SARIMA (30 Dias)")
    
    corte_hist = df_historico.tail(janela_historica_dias).copy()
    
    fig = go.Figure()

    # 1. Histórico Real (Cinza Prateado / Slate)
    fig.add_trace(go.Scatter(
        x=corte_hist.index,
        y=corte_hist["usd_brl"],
        mode="lines",
        name="Histórico Real (BCB)",
        line=dict(color="#94a3b8", width=2)
    ))

    # Ponto de junção entre histórico e forecast
    ultima_data = corte_hist.index[-1]
    ultimo_valor = corte_hist["usd_brl"].iloc[-1]
    x_proj = [ultima_data] + list(df_forecast.index)
    y_proj = [ultimo_valor] + list(df_forecast["yhat"])
    y_upper = [ultimo_valor] + list(df_forecast["limite_superior"])
    y_lower = [ultimo_valor] + list(df_forecast["limite_inferior"])

    # 2. Banda de Confiança (Sombreado Azul Celeste translúcido)
    fig.add_trace(go.Scatter(
        x=x_proj + x_proj[::-1],
        y=y_upper + y_lower[::-1],
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.12)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="Intervalo de Confiança (80%)"
    ))

    # 3. Curva da Previsão SARIMA (Azul Celeste Neon)
    fig.add_trace(go.Scatter(
        x=x_proj,
        y=y_proj,
        mode="lines",
        name="Previsão SARIMA",
        line=dict(color="#38bdf8", width=3, dash="dash")
    ))

    # Customização do Layout Plotly (Dark Theme Industrial)
    fig.update_layout(
        paper_bgcolor="rgba(11, 15, 25, 0)",
        plot_bgcolor="rgba(17, 24, 39, 0.6)",
        font=dict(color="#cbd5e1", family="sans-serif"),
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.1)",
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(148, 163, 184, 0.1)",
            zeroline=False,
            tickprefix="R$ "
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)