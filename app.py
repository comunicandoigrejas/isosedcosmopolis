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

# --- 3. ESTILIZAÇÃO CSS (Layout Estilo App Mobile) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões Estilo Pill (Inspirado no exemplo enviado) */
    div.stButton > button {
        width: 100%;
        height: 75px;
        border-radius: 50px; /* Arredondamento total */
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
        transition: 0.3s;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    
    /* Cores individuais para cada botão para facilitar a visualização */
    /* Agenda */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3; } 
    /* Mídia e Recepção */
    div.stButton:nth-of-type(2) > button { background-color: #e17055; }
    /* Departamentos */
    div.stButton:nth-of-type(3) > button { background-color: #00b894; }
    /* Devocional */
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7; }

    div.stButton > button:hover {
        transform: scale(1.03);
        filter: brightness(1.2);
    }
    
    /* Estilo do Botão Voltar */
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px;
        font-size: 14px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* Cards de Informação */
    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 20px;
        border-left: 6px solid #00ffcc;
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BANCO DE DADOS (Rigorosamente Mantido) ---
agenda_completa_2026 = {
    "Janeiro": ["16/01 (Sex) – 🧑‍🎓 Jovens", "18/01 (Dom) – 🌍 Culto de Missões", "23/01 (Sex) – 👔 Varões", "30/01 (Sex) – 🎤 Louvor", "31/01 (Sáb) – 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02 (Sex) – 👗 Irmãs", "13/02 (Sex) – 🧑‍🎓 Jovens", "14 a 17/02 – 🚌 Retiro", "28/02 (Sáb) – 🙏 Tarde com Deus"]
}

# Escalas de Mídia
escala_midia = [
    {"data": "01/02", "op": "Júnior", "foto": "Tiago (17:30)"},
    {"data": "04/02", "op": "Lucas", "foto": "Grazi (19:00)"},
    {"data": "06/02", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "08/02", "op": "Lucas", "foto": "Grazi (17:30)"}
]

# Escala Recepção
escala_recepcao = [
    {"data": "04/02", "dia": "Quarta", "dupla": "Ailton e Rita"},
    {"data": "06/02", "dia": "Sexta", "dupla": "Márcia e Felipe"},
    {"data": "08/02", "dia": "Dom", "dupla": "Simone e Elisabete"}
]

# --- 5. NAVEGAÇÃO E HUB ---

if st.session_state.pagina == "Início":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("⛪ ISOSED Cosmópolis")
    st.write("Selecione uma opção:")
    st.markdown("---")

    # Botões em lista vertical para visualização limpa
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Agenda 2026")
    for mes, evs in agenda_completa_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia e Recepção")
    t_midia, t_recep = st.tabs(["📷 Mídia", "🤝 Recepção"])
    
    with t_midia:
        for it in escala_midia:
            st.markdown(f'<div class="card-escala"><b>{it["data"]}</b><br>🎧 Som: {it["op"]} | 📸 Foto: {it["foto"]}</div>', unsafe_allow_html=True)
    
    with t_recep:
        for it in escala_recepcao:
            st.markdown(f'<div class="card-escala"><b>{it["data"]} ({it["dia"]})</b><br>👥 Dupla: {it["dupla"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    st.info("Aqui constam as programações das Irmãs, Jovens, Varões, Kids e Missões.")

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Devocional")
