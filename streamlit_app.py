import streamlit as st
import requests
from datetime import datetime
import uuid
import pandas as pd 

N8N_WEBHOOK_URL = "http://193.136.11.144:5624/webhook-test/d690d22d-3ff1-481a-9b57-a0fc52d2404f"

#teste

st.title("🏥 Chat de Agendas Médicas")
st.write("Consulte agendamentos a partir de hoje.")

if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        if "content" in msg and msg["content"]:
            st.write(msg["content"])
        if "tabela" in msg and msg["tabela"] is not None:
            df = pd.DataFrame(msg["tabela"])
            st.dataframe(df, use_container_width=True)

pergunta = st.chat_input("Faça uma pergunta sobre a agenda")

if pergunta:
    st.session_state.historico.append({"role": "user", "content": pergunta})

    with st.chat_message("user"):
        st.write(pergunta)

    agora = datetime.now()

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())


    payload = {
        "mensagem": pergunta,
        "data_hoje": agora.date().isoformat(),
        "data_hora_pedido": agora.isoformat(),
        "origem": "streamlit-medicos",
        "tipo": "consulta_agenda",
        "sessionId": st.session_state.session_id
    }

    resposta_bot = "O n8n respondeu sem conteúdo."
    tabela_bot = None

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=60*4)
        response.raise_for_status()

        dados = response.json()

        st.json(dados)
        if "resposta" in dados and dados["resposta"]:
            resposta_bot = dados.get("resposta", "O n8n respondeu sem o campo 'resposta'.")

        if "tabela" in dados and isinstance(dados["tabela"], list):
            tabela_bot = dados["tabela"]

        if not resposta_bot and tabela_bot:
            resposta_bot = "Encontrei os registos da agenda."

    except Exception as e:
        resposta_bot = f"Erro ao comunicar com o n8n: {e}"

    st.session_state.historico.append({
        "role": "assistant",
        "content": resposta_bot,
        "tabela": tabela_bot
    })

    with st.chat_message("assistant"):
        st.write(resposta_bot)
        if tabela_bot is not None:
            df = pd.DataFrame(tabela_bot)
            st.dataframe(df, use_container_width=True)

    with st.expander("JSON enviado ao n8n"):
        st.json(payload)