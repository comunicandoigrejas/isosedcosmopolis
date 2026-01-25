import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ISOSED Cosmópolis - App Oficial",
    page_icon="⛪",
    layout="wide"
)

# --- 2. ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
    }
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
    }
    .card-destaque {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00b09b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (Ajuste do nome da imagem) ---
with st.sidebar:
    # Nome ajustado conforme solicitado
    nome_logo = "logo igreja.png" 
    
    if os.path.exists(nome_logo):
        st.image(nome_logo, width=200)
    else:
        st.title("⛪ ISOSED")
        st.caption("Cosmópolis - SP")
        st.warning(f"Certifique-se de que o arquivo se chama: {nome_logo}")
    
    st.markdown("---")
    menu = st.sidebar.radio(
        "Navegação",
        ["Início", "Agenda 2026", "Redes Sociais", "Departamentos", "Devocional"]
    )

# --- 4. CONTEÚDO DAS PÁGINAS ---

if menu == "Início":
    st.title("Portal Igreja Só o Senhor é Deus")
    
    # Horários Atualizados
    st.subheader("📍 Nossos Cultos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("✨ **Domingos**\n\n Às 18h00")
    with col2:
        st.info("📖 **Quartas-feiras**\n\n Às 19h30")
    with col3:
        st.info("🔥 **Sextas-feiras**\n\n Às 19h30")

elif menu == "Agenda 2026":
    st.title("🗓️ Agenda de Departamentos 2026")
    # Tabela com as datas dos departamentos
    dados = [
        {"Mês": "Janeiro", "Irmãs": "-", "Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
        {"Mês": "Fevereiro", "Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
        {"Mês": "Março", "Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
        {"Mês": "Abril", "Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
        {"Mês": "Maio", "Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
    ]
    st.table(pd.DataFrame(dados))

# (As demais seções como Departamentos e Redes Sociais permanecem estruturadas)
