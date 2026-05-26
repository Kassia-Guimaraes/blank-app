import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render_kpis(metricas):
    agendadas = metricas.get("Cirurgias Agendadas", 0)
    espera = metricas.get("Cirurgias Lista de Espera", 0)
    recursos = float(metricas.get("Recursos", 0))
    turnos = metricas.get("Turnos desrespeitados", 0)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Cirurgias Agendadas", agendadas)
    c2.metric("Lista de Espera", espera)
    c4.metric("Turnos Desrespeitados", turnos)

    cor = "red" if recursos > 90 else "green"
    c3.markdown(
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
            "Agendadas": "#2E86DE",
            "Lista de Espera": "#E67E22"
        }
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))

    return fig


def grafico_pizza_recursos(metricas):
    recursos = float(metricas.get("Recursos", 0))
    livre = max(0, 100 - recursos)

    df = pd.DataFrame({
        "Categoria": ["Utilizados", "Livres"],
        "Valor": [recursos, livre]
    })

    cor_utilizados = "#E74C3C" if recursos > 90 else "#27AE60"

    fig = px.pie(
        df,
        names="Categoria",
        values="Valor",
        title="Utilização dos Recursos",
        hole=0.45,
        color="Categoria",
        color_discrete_map={
            "Utilizados": cor_utilizados,
            "Livres": "#D5DBDB"
        }
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))

    return fig


def render_graficos(metricas):
    col1, col2 = st.columns(2)

    with col1:
        fig1 = grafico_pizza_cirurgias(metricas)
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = grafico_pizza_recursos(metricas)
        st.plotly_chart(fig2, use_container_width=True)