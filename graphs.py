import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_kpis(metricas):
    agendadas = metricas.get("Cirurgias Agendadas", 0)
    espera = metricas.get("Cirurgias Lista de Espera", 0)
    recursos = float(metricas.get("Recursos", metricas.get("Recurusos", 0)))
    turnos = metricas.get("Turnos desrespeitados", metricas.get("Turnos desreipeitados", 0))

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Cirurgias Agendadas", agendadas)
    c2.metric("Lista de Espera", espera)
    c3.metric("Turnos Desrespeitados", turnos)

    cor = "red" if recursos > 90 else "green"
    c4.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 12px;
            background-color: #f8f9fa;
            border-left: 8px solid {cor};
            text-align: center;
        ">
            <div style="font-size: 0.95rem; color: gray;">Recursos</div>
            <div style="font-size: 2rem; font-weight: bold; color: {cor};">
                {recursos:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def grafico_pizza_cirurgias(metricas):
    agendadas = metricas.get("Cirurgias Agendadas", 0)
    espera = metricas.get("Cirurgias Lista de Espera", 0)

    df = pd.DataFrame({
        "Categoria": ["Agendadas", "Lista de Espera"],
        "Valor": [agendadas, espera]
    })

    fig = px.pie(
        df,
        names="Categoria",
        values="Valor",
        title="Distribuição de Cirurgias",
        hole=0.45,
        color="Categoria",
        color_discrete_map={
            "Agendadas": "#5BB042",
            "Lista de Espera": "#C65D5D"
        }
    )

    fig.update_traces(textinfo="percent+label", textposition="outside")
    fig.update_layout(
            height=400,
            margin=dict(t=100, b=30, l=40, r=40),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.9,
                xanchor="left",
                x=1.02
            )
        )

    return fig