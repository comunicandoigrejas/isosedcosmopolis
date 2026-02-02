import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 3. ESTILIZAÇÃO CSS (Clean App e Alinhamento de Botões) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões Padronizados - Tamanho Único para Alinhamento */
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1); color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-size: 20px; font-weight: bold; transition: 0.3s;
        display: flex; align-items: center; justify-content: center;
    }
    div.stButton > button:hover {
        background-color: #00ffcc; color: #302b63; transform: scale(1.02);
    }
    
    .btn-voltar div.stButton > button {
        height: 60px; font-size: 18px; margin-bottom: 20px;
    }

    /* Estilos de Cards */
    .data-item {
        background: rgba(0, 0, 0, 0.3); padding: 8px 15px;
        border-radius: 5px; margin-bottom: 5px; border-left: 4px solid #00ffcc;
    }
    .card-escala {
        background: rgba(0, 0, 0, 0.3); padding: 15px;
        border-radius: 12px; border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS (Mantidos Rigorosamente) ---
# Escala Recepção Fevereiro
escala_recepcao = [
    {"data": "04/02", "dia": "Quarta", "dupla": "Ailton e Rita"},
    {"data": "06/02", "dia": "Sexta", "dupla": "Márcia e Felipe"},
    {"data": "08/02", "dia": "Domingo", "dupla": "Simone e Elisabete"},
    {"data": "11/02", "dia": "Quarta", "dupla": "Ceia e Felipe"},
    {"data": "13/02", "dia": "Sexta", "dupla": "Ailton e Márcia"},
    {"data": "15/02", "dia": "Domingo", "dupla": "Rita e Simone"},
    {"data": "18/02", "dia": "Quarta", "dupla": "Ceia e Elisabete"},
    {"data": "20/02", "dia": "Sexta", "dupla": "Felipe e Márcia"},
    {"data": "22/02", "dia": "Domingo", "dupla": "Ailton e Simone"},
    {"data": "28/02", "dia": "Sábado", "dupla": "Ceia e Rita ✨"}
]

# Escala Mídia Fevereiro
escala_midia = [
    {"data": "01/02", "culto": "Família", "op": "Júnior", "foto": "Tiago (17:30)"},
    {"data": "04/02", "culto": "Quarta", "op": "Lucas", "foto": "Grazi (19:00)"},
    {"data": "06/02", "culto": "Sexta", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "08/02", "culto": "Santa Ceia", "op": "Lucas", "foto": "Grazi (17:30)"},
    {"data": "11/02", "culto": "Quarta", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "13/02", "culto": "Sexta", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "15/02", "culto": "Missões", "op": "Samuel", "foto": "Tiago (17:30)"},
    {"data": "18/02", "culto": "Quarta", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "20/02", "culto": "Sexta", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "22/02", "culto": "Família", "op": "Nicholas", "foto": "Grazi (17:30)"},
    {"data": "25/02", "culto": "Quarta", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "27/02", "culto": "Sexta", "op": "Samuel", "foto": "Grazi (19:00)"},
    {"data": "28/02", "culto": "Tarde com Deus", "op": "Nicholas", "foto": "Tiago (14:30)"}
]

# --- 5. NAVEGAÇÃO E PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br><br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 4])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Selecione uma área abaixo:")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        # NOME DO BOTÃO ALTERADO CONFORME PEDIDO
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    with col2:
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia e Recepção")
    
    t_escala_midia, t_escala_recepcao = st.tabs(["📷 Escala de Mídia", "🤝 Escala de Recepção"])
    
    with t_escala_midia:
        st.subheader("Escala de Fevereiro/2026")
        for item in escala_midia:
            st.markdown(f'<div class="card-escala"><b>{item["data"]} - {item["culto"]}</b><br>🎧 Som: {item["op"]} | 📸 Foto: {item["foto"]}</div>', unsafe_allow_html=True)
    
    with t_escala_recepcao:
        st.subheader("Escala da Recepção - Fevereiro/2026")
        for item in escala_recepcao:
            st.markdown(f'<div class="card-escala"><b>{item["data"]} ({item["dia"]})</b><br>👥 Dupla: {item["dupla"]}</div>', unsafe_allow_html=True)

# [As outras páginas: Agenda, Departamentos e Devocional seguem a mesma lógica aprovada]
