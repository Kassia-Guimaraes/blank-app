import streamlit as st
import requests
from datetime import datetime
import uuid
import pandas as pd 

import plotly.express as px
import plotly.graph_objects as go

N8N_WEBHOOK_URL = "http://193.136.11.144:5624/webhook-test/99a9a512-1f7f-4fbb-ad58-2deefed82045"


st.title("🏥 Chat de Agendas Médicas")
st.write("Consulte agendamentos a partir de hoje.")

##### histórico das conversas #######
if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if "content" in msg and msg["content"]:
            st.write(msg["content"])
        if "tabela" in msg and msg["tabela"] is not None:
            df = pd.DataFrame(msg["tabela"])
            st.dataframe(df, use_container_width=True)
        if "metricas" in msg and msg['metricas'] is not None:
            print('')


sugestoes = [ #sugestões de questões
    "Consultar a lista de espera",
    "Consultar as últimas cirurgias",
    "Realizar um agendamento para os dias 10 a 20 de março de 2023",
    "Qual a quantidade de pacientes por médico?",
    "Alterar agendamentos"
]

sugest = st.pills(
        "Sugestões de perguntas",
        sugestoes,
        selection_mode="single"
    )

##### input do utilizador ######
pergunta_dig = st.chat_input("Escreva a sua pergunta")

pergunta = sugest or pergunta_dig

if pergunta:
    st.session_state.historico.append({"role": "user", "content": pergunta})

    with st.chat_message("user"):
        st.write(pergunta)

    agora = datetime.now()

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


    payload = {
        "chatInput": pergunta,
        "data_hoje": agora.date().isoformat(),
        "data_hora_pedido": agora.isoformat(),
        "origem": "streamlit-medicos",
        "tipo": "consulta_agenda",
        "sessionId": st.session_state.session_id
    }

    resposta_bot = "O n8n respondeu sem conteúdo."
    tabela_bot = None

    try:
        with st.spinner("A aguardar resposta...", show_time=True):
            inicio = datetime.now()
            response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60*20)
            response.raise_for_status()
            dados = response.json()


        if "output" in dados and dados["output"]:
            resposta_bot = dados.get("output", "O n8n respondeu sem o campo 'resposta'.")

        if "tabela" in dados and isinstance(dados["tabela"], list):
            tabela_bot = dados["tabela"]

        if "metricas" in dados and dados['metricas']:
            metricas_bot = dados['metricas']

        if not resposta_bot and tabela_bot:
            resposta_bot = "Encontrei os registos da agenda."

    except Exception as e:
        resposta_bot = f"Erro ao comunicar com o n8n: {e}"

    st.session_state.historico.append({
        "role": "assistant",
        "content": resposta_bot,
        "tabela": tabela_bot,
        "metricas": metricas_bot
    })

    with st.chat_message("assistant"):
        st.write(resposta_bot)
        if metricas_bot:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Cirurgias Agendadas", metricas_bot.get("Cirurgias Agendadas", 0))
            c2.metric("Lista de Espera", metricas_bot.get("Cirurgias Lista de Espera", 0))
            c3.metric("Recursos", f"{metricas_bot.get('Recursos', 0):.2f}%")
            c4.metric("Turnos Desrespeitados", metricas_bot.get("Turnos desrespeitados", 0))
        if tabela_bot is not None:
            df = pd.DataFrame(tabela_bot)
            st.dataframe(df, use_container_width=True)