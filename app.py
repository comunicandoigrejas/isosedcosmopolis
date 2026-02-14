import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Lógica Aniversariantes: Domingo a Segunda
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=0#gid=0"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. ESTILO CSS (Foco em Azul Escuro e Contraste) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* FORÇAR TÍTULOS EM BRANCO */
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
    }

    /* ESTILO DOS BOTÕES - AZUL ESCURO UNIFICADO */
    button[data-testid="stBaseButton-secondary"] {
        width: 150px !important;
        height: 65px !important;
        background-color: #0a3d62 !important; /* AZUL ESCURO */
        border-radius: 12px !important;
        border: 2px solid #3c6382 !important; /* Borda levemente mais clara */
        box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: 0.3s;
    }

    /* FORÇAR TEXTO BRANCO EM TODOS OS BOTÕES */
    button[data-testid="stBaseButton-secondary"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }

    /* Efeito ao passar o mouse */
    button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #3c6382 !important;
        border-color: #FFFFFF !important;
        transform: translateY(-2px);
    }

    /* CARDS DE ANIVERSÁRIO */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ROTEADOR DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes da Semana
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu Principal Azul Escuro
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.button("🗓️ Agenda", key="bt_ag", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", key="bt_gr", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", key="bt_an", on_click=navegar, args=("Aniversariantes",))
    with c2:
        st.button("📢 Escalas", key="bt_es", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", key="bt_me", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", key="bt_le", on_click=navegar, args=("Leitura",))
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=200)
t.markdown('</div>', unsafe_allow_html=True)
