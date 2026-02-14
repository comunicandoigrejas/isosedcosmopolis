import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

# Domingo passado até Segunda que vem
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO (Sem rerun no callback) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVAcqFcPK0/edit"

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

# --- 4. CSS PARA VISIBILIDADE (FORÇANDO CONTRASTE) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* ESTILO DOS BOTÕES - FORÇANDO TEXTO PRETO OU BRANCO */
    div.stButton > button {
        width: 140px !important; height: 60px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
    }

    /* O SEGREDO: Focar no parágrafo interno que o Streamlit gera */
    div.stButton > button p {
        font-weight: 900 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
    }

    /* CLASSES DE COR */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-blue p { color: white !important; }

    .btn-orange button { background-color: #e17055 !important; }
    .btn-orange p { color: white !important; }

    .btn-green button { background-color: #00b894 !important; }
    .btn-green p { color: white !important; }

    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-purple p { color: white !important; }

    .btn-red button { background-color: #ff7675 !important; }
    .btn-red p { color: white !important; }

    .btn-yellow button { background-color: #f1c40f !important; }
    .btn-yellow p { color: black !important; } /* Texto preto no fundo amarelo */

    .card-niver {
        width: 145px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        text-align: center !important; margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; }
    .niver-data { font-size: 0.95em !important; font-weight: bold; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center; color: white;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes (Mariane e Fátima juntas)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        
        if aniv_f:
            st.markdown("<p style='text-align:center; color:#ffd700; font-weight:bold;'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            cols_aniv = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols_aniv[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu e Logo
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="ag", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        st.button("👥 Grupos", key="gr", on_click=navegar, args=("Grupos",))
        st.markdown('</div><div class="btn-yellow">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="an", on_click=navegar, args=("AnivGeral",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="es", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="me", on_click=navegar, args=("Meditar",))
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="le", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=180)

# BLOCOS DAS PÁGINAS (MUITO IMPORTANTE PARA OS BOTÕES FUNCIONAREM)
elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditar")
    # ... código do devocional com Aplicação e Desafio ...

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📜 Leitura Bíblica")

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda")

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Grupos")

elif st.session_state.pagina == "AnivGeral":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🎂 Aniversariantes")
