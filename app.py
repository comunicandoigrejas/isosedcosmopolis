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

# Lógica: Domingo desta semana até Segunda da próxima
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA (⚠️ COLOQUE SEU LINK AQUI) ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=504320066#gid=504320066"

def carregar_dados(aba):
    try:
        if "google.com" not in URL_PLANILHA:
            st.error("⚠️ O link da planilha não foi configurado corretamente.")
            return pd.DataFrame()
            
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Erro ao acessar a aba '{aba}': {e}")
        return pd.DataFrame()

# --- 3. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): 
    st.session_state.pagina = p

# --- 4. ESTILO CSS (O "Tanque de Guerra" contra o Branco no Branco) ---
st.markdown("""
    <style>
    /* Esconde elementos do Streamlit */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    
    /* Força o fundo escuro do App */
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* SELETOR ULTRA-FORTE PARA OS BOTÕES */
    /* Isso garante que o fundo seja colorido e a letra branca/preta */
    div[data-testid="stButton"] > button {
        width: 140px !important;
        height: 60px !important;
        border-radius: 12px !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        font-size: 11px !important;
    }

    /* Definindo as Cores por "Ordem de Aparecimento" */
    /* Agenda (Azul) */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) div[data-testid="stButton"] > button { background-color: #0984e3 !important; color: white !important; }
    /* Escalas (Laranja) */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) div[data-testid="stButton"] > button { background-color: #e17055 !important; color: white !important; }
    
    /* Se os seletores acima falharem, este bloco abaixo é o Plano B (Garante a leitura) */
    .stButton button p { color: white !important; font-weight: 900 !important; }
    
    /* CARD DE ANIVERSÁRIO - CENTRALIZAÇÃO TOTAL */
    .card-niver {
        width: 145px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important; /* Centraliza na coluna */
        text-align: center !important;
    }
    .niver-nome { font-size: 0.9em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; padding: 0 5px; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: #FFFFFF !important; margin-top: 5px; }
    
    .titulo-semana { font-size: 1.2em; font-weight: 800; color: #ffd700; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center; color: white;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # 1. ANIVERSARIANTES (Lógica Domingo a Segunda)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        # Filtro de data
        aniv_list = []
        for _, r in df_n.iterrows():
            try:
                d_aniv = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= d_aniv <= segunda_proxima:
                    aniv_list.append(r)
            except: continue
        
        if aniv_list:
            st.markdown("<p class='titulo-semana'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            # Organiza Mariane e Fátima lado a lado
            cols = st.columns(len(aniv_list) if len(aniv_list) <= 4 else 4)
            for idx, p in enumerate(aniv_list):
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="card-niver">
                            <div class="niver-nome">{p['nome']}</div>
                            <div class="niver-data">{int(p['dia']):02d}/{int(p['mes']):02d}</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MENU + LOGO (Aproximados e com Cores Forçadas)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    
    with c1:
        # Agenda
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #0984e3 !important; color: white !important; }</style>', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="btn_agenda")
        
        # Grupos
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #00b894 !important; color: white !important; }</style>', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",), key="btn_grupos")
        
        # Aniversários
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #f1c40f !important; color: black !important; }</style>', unsafe_allow_html=True)
        st.button("🎂 Anivers.", on_click=navegar, args=("Aniversariantes",), key="btn_aniv")

    with c2:
        # Escalas
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #e17055 !important; color: white !important; }</style>', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="btn_escalas")
        
        # Meditar
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #6c5ce7 !important; color: white !important; }</style>', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",), key="btn_meditar")
        
        # Leitura
        st.markdown('<style>div[data-testid="stButton"] button { background-color: #ff7675 !important; color: white !important; }</style>', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="btn_leitura")

    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=200)
