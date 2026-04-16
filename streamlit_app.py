import streamlit as st
import requests
from datetime import datetime

#N8N_WEBHOOK_URL = "https://TEU-N8N/webhook/agendamento-hospitalar"

st.title("🏥 Chat de Agendas Médicas")
st.write("Consulte agendamentos a partir de hoje.")

if "historico" not in st.session_state:
    st.session_state.historico = []

for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

pergunta = st.chat_input("Faça uma pergunta sobre a agenda")

if pergunta:
    st.session_state.historico.append({"role": "user", "content": pergunta})

    with st.chat_message("user"):
        st.write(pergunta)

    agora = datetime.now()

    payload = {
        "mensagem": pergunta,
        "data_hoje": agora.date().isoformat(),
        "data_hora_pedido": agora.isoformat(),
        "origem": "streamlit-medicos",
        "tipo": "consulta_agenda"
    }

    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        response.raise_for_status()

        dados = response.json()
        resposta_bot = dados.get("resposta", "O n8n respondeu sem o campo 'resposta'.")

    except Exception as e:
        resposta_bot = f"Erro ao comunicar com o n8n: {e}"

    st.session_state.historico.append({"role": "assistant", "content": resposta_bot})

    with st.chat_message("assistant"):
        st.write(resposta_bot)

    with st.expander("JSON enviado ao n8n"):
        st.json(payload)