import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta
import pytz
import os

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

# Lógica: Domingo que passou até Segunda que vem
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO (O "Cérebro" do App) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA (Link Salvo) ---
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

# --- 4. CSS NUCLEAR (Forçando Cores e Fontes) ---
st.markdown("""
    <style>
    /* Forçar Fundo Escuro */
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }

    /* FORÇAR TEXTO DOS CABEÇALHOS EM BRANCO */
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { 
        color: #FFFFFF !important; 
    }

    /* ESTILO DOS BOTÕES - ALTA PRIORIDADE */
    button[data-testid="stBaseButton-secondary"] {
        width: 150px !important;
        height: 65px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* FORÇAR COR DA FONTE DENTRO DOS BOTÕES (Resolve o "branco no branco") */
    button[data-testid="stBaseButton-secondary"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }

    /* CORES DE FUNDO POR BOTÃO (Usando classes de div para isolar) */
    .c-ag button { background-color: #0984e3 !important; }
    .c-gr button { background-color: #00b894 !important; }
    .c-es button { background-color: #e17055 !important; }
    .c-me button { background-color: #6c5ce7 !important; }
    .c-le button { background-color: #ff7675 !important; }
    .c-an button { background-color: #f1c40f !important; }
    .c-an button p { color: #000000 !important; } /* Texto preto no amarelo */

    /* Cards de Aniversário */
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

# PÁGINA INICIAL
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes (Domingo a Segunda)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = [r for _, r in df_n.iterrows() if domingo_atual <= datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date() <= segunda_proxima]
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu e Logo
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="c-ag">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="b1", on_click=navegar, args=("P_Agenda",))
        st.markdown('</div><div class="c-gr">', unsafe_allow_html=True)
        st.button("👥 Grupos", key="b2", on_click=navegar, args=("P_Grupos",))
        st.markdown('</div><div class="c-an">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="b3", on_click=navegar, args=("P_Aniv",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="c-es">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="b4", on_click=navegar, args=("P_Escalas",))
        st.markdown('</div><div class="c-me">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="b5", on_click=navegar, args=("P_Meditar",))
        st.markdown('</div><div class="c-le">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="b6", on_click=navegar, args=("P_Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=200)

# PÁGINAS DE DESTINO (O que faz o botão funcionar)
elif st.session_state.pagina == "P_Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty: st.dataframe(df, use_container_width=True)

elif st.session_state.pagina == "P_Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "P_Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "P_Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Devocional</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "P_Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "P_Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Todos os Aniversariantes</h1>", unsafe_allow_html=True)
