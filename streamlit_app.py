import streamlit as st

st.title("🎈 Bem-vindo!")
st.write("Chat para Agendamentos Hospitalares.")

texto = st.text_input("Escreva aqui:")

if texto:
    st.json({
        "mensagem": texto
    })
