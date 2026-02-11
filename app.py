import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO SEGURA (SaaS Ready) ---
# O Streamlit buscará as credenciais automaticamente em .streamlit/secrets.toml
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_escalas(nome_aba):
    try:
        # Busca os dados da planilha usando o mapeamento definido nos secrets
        # A URL da planilha agora fica protegida nos secrets do sistema
        df = conn.read(worksheet=nome_aba, ttl="10m")
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria Total de Início ao Fim) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }

    /* CONTAINER CENTRALIZADO PARA ALINHAMENTO */
    .button-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 10px;
    }

    /* BOTÕES PILL - Largura fixa (100% do container) e alinhamento total */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        transition: 0.3s !important;
        text-transform: uppercase !important;
        margin-bottom: 20px !important;
        display: block !important;
    }

    /* Cores do Menu */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 20px rgba(255,255,255,0.2) !important;
    }

    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important; border-radius: 25px !important; font-size: 14px !important;
    }

    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 15px;
    }
    .card-escala b { color: #00ffcc; }
    .horario { color: #ffd700; font-weight: bold; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DADOS DA AGENDA 2026 (Preservados) ---
agenda_2026 = {
    "Janeiro": ["16/01: 🧑‍🎓 Jovens", "18/01: 🌍 Missões", "23/01: 👔 Varões", "30/01: 🎤 Louvor", "31/01: 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02: 👗 Irmãs", "13/02: 🧑‍🎓 Jovens", "15/02: 🌍 Missões", "20/02: 👔 Varões", "27/02: 🎤 Louvor", "28/02: 🙏 Tarde com Deus"],
    "Março": ["06/03: 👗 Irmãs", "13/03: 🧑‍🎓 Jovens", "15/03: 🌍 Missões", "20/03: 👔 Varões", "27/03: 🎤 Louvor", "28/03: 🙏 Tarde com Deus"]
}

# --- 6. NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=110)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Escalas de Fevereiro")
    
    t_mid, t_rec = st.tabs(["📷 Mídia e Som", "🤝 Recepção"])
    
    with t_mid:
        df = carregar_escalas("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r["data"]} - {r["culto"]}</b><br>🎧 {r["op"]} | 📸 {r["foto"]}<br><span class="horario">⏰ Chegada: {r["chegada"]}</span></div>', unsafe_allow_html=True)
        else:
            st.error("Erro ao carregar dados. Verifique a aba 'Midia' na planilha.")

    with t_rec:
        df = carregar_escalas("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r["data"]} ({r.get("dia", "")})</b><br>👥 Dupla: {r["dupla"]}<br><span class="horario">⏰ Chegada: {r["chegada"]}</span></div>', unsafe_allow_html=True)
        else:
            st.error("Erro ao carregar dados. Verifique a aba 'Recepcao' na planilha.")

# [As outras páginas: Agenda, Departamentos e Devocional seguem o mesmo padrão]
