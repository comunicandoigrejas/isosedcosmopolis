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

# Domingo desta semana até Segunda da próxima
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
# O link capturado na sua imagem
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=504320066#gid=504320066"

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

# --- 3. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS (O Segredo para acabar com o Branco no Branco) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; color: white !important; }

    /* ESTILO DOS BOTÕES */
    div.stButton > button {
        width: 135px !important; height: 60px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        display: block !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }

    /* FORÇAR COR DA FONTE (Foca no elemento P interno do Streamlit) */
    div.stButton > button p {
        color: white !important;
        font-weight: 900 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
    }

    /* CORES DE FUNDO ESPECÍFICAS */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-orange button { background-color: #e17055 !important; }
    .btn-green button { background-color: #00b894 !important; }
    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-red button { background-color: #ff7675 !important; }
    /* Aniversários: Amarelo com letra preta para contraste */
    .btn-yellow button { background-color: #f1c40f !important; }
    .btn-yellow button p { color: black !important; }

    /* CARDS DE ANIVERSÁRIO (Centralizados conforme imagem d918ca) */
    .card-niver {
        width: 140px !important; height: 85px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 0.9em !important; font-weight: bold; color: white; margin-top: 5px; }

    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # ANIVERSARIANTES
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                d_a = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= d_a <= segunda_proxima: aniv_f.append(r)
            except: continue
        
        if aniv_f:
            st.markdown("<p style='text-align:center; color:#ffd700; font-weight:bold;'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            # Aproxima os cards no centro (corrige image_d918ca)
            _, c_n1, c_n2, _ = st.columns([1, 2, 2, 1])
            with c_n1:
                st.markdown(f'<div class="card-niver"><div class="niver-nome">{aniv_f[0]["nome"]}</div><div class="niver-data">{int(aniv_f[0]["dia"]):02d}/{int(aniv_f[0]["mes"]):02d}</div></div>', unsafe_allow_html=True)
            with c_n2:
                if len(aniv_f) > 1:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{aniv_f[1]["nome"]}</div><div class="niver-data">{int(aniv_f[1]["dia"]):02d}/{int(aniv_f[1]["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # MENU E LOGO (Conforme image_d96aa4)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2.5])
    with c1:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-yellow">', unsafe_allow_html=True)
        st.button("🎂 Aniv.", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        # Logo da igreja (globo com chamas) conforme imagem
        if os.path.exists("logo igreja.png"): 
            st.image("logo igreja.png", use_container_width=True)
