import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM O GOOGLE SHEETS ---
# Substitua pela URL da sua planilha pública
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/SUA_ID_AQUI/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_escalas(aba):
    try:
        # Tenta ler a aba específica da planilha
        return conn.read(spreadsheet=URL_PLANILHA, worksheet=aba)
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria Total e Design Pill) ---
st.markdown("""
    <style>
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

    /* Botões Pill Sincronizados (Simetria Vertical e Alinhamento Total) */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.3s !important;
        text-transform: uppercase !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 15px !important;
    }
    
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    div.stButton > button:hover { transform: scale(1.02) !important; filter: brightness(1.1) !important; }
    
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important; border-radius: 30px; font-size: 14px;
    }

    /* Cards de Escala com destaque para o Horário */
    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; font-size: 1.1rem; }
    .horario-chegada { color: #ffd700; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BANCO DE DADOS AGENDA (MANUAL) ---
agenda_2026 = {
    "Janeiro": ["16/01: 🧑‍🎓 Jovens", "18/01: 🌍 Missões", "23/01: 👔 Varões", "30/01: 🎤 Louvor", "31/01: 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02: 👗 Irmãs", "13/02: 🧑‍🎓 Jovens", "15/02: 🌍 Missões", "20/02: 👔 Varões", "27/02: 🎤 Louvor", "28/02: 🙏 Tarde com Deus"],
    # ... demais meses conforme o histórico aprovado
}

# --- 6. NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Sincronizado com Google Sheets")

    st.markdown("<br>", unsafe_allow_html=True)
    col_central = st.columns([1, 5, 1])[1]
    with col_central:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("📢 Escalas de Fevereiro")
    t_mid, t_rec = st.tabs(["📷 Mídia e Som", "🤝 Recepção"])
    
    with t_mid:
        df_midia = carregar_escalas("Midia")
        if not df_midia.empty:
            for _, row in df_midia.iterrows():
                st.markdown(f"""
                <div class="card-escala">
                    <b>{row['data']} - {row['culto']}</b><br>
                    🎧 Som: {row['op']} | 📸 Foto: {row['foto']}<br>
                    <span class="horario-chegada">⏰ Chegada da equipe: {row['chegada']}</span>
                </div>
                """, unsafe_allow_html=True)

    with t_rec:
        df_recepcao = carregar_escalas("Recepcao")
        if not df_recepcao.empty:
            for _, row in df_recepcao.iterrows():
                st.markdown(f"""
                <div class="card-escala">
                    <b>{row['data']} ({row['dia']})</b><br>
                    👥 Dupla: {row['dupla']}<br>
                    <span class="horario-chegada">⏰ Chegada da equipe: {row['chegada']}</span>
                </div>
                """, unsafe_allow_html=True)

# [As outras páginas: Agenda, Departamentos e Devocional mantêm a lógica anterior]
