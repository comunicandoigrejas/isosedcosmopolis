import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=0#gid=0"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS (Ajustes de Fonte e Layout) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .main-wrapper { max-width: 520px; margin: 0 auto; padding: 5px; }

    /* BOTÕES E CARDS (130x55) */
    div.stButton > button, .card-niver {
        width: 130px !important; 
        height: 55px !important; 
        border-radius: 12px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        margin-bottom: 10px !important; 
    }

    div.stButton > button {
        font-size: 11px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
    }

    .btn-1 button { background-color: #0984e3 !important; } .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; } .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; } .btn-6 button { background-color: #ff7675 !important; }

    .card-niver {
        background: rgba(255, 215, 0, 0.1) !important;
        border: 1px solid #ffd700 !important;
        margin-bottom: 10px !important;
    }

    /* Distâncias Simétricas (10px total H/V) */
    .btn-left div.stButton > button { margin-left: auto !important; margin-right: 5px !important; }
    .btn-right div.stButton > button { margin-right: auto !important; margin-left: 5px !important; }

    .niver-left { display: flex; justify-content: flex-end; margin-right: 5px; }
    .niver-right { display: flex; justify-content: flex-start; margin-left: 5px; }

    /* --- AJUSTE DE FONTE DOS ANIVERSARIANTES --- */
    .niver-nome { 
        font-size: 0.95em !important; /* Aumentado de 0.8em para 0.95em */
        font-weight: 900; 
        color: #ffd700; 
        text-transform: uppercase; 
        text-align: center; 
        line-height: 1; 
    }
    .niver-data { font-size: 0.7em !important; opacity: 0.8; margin-top: 3px; }

    [data-testid="column"] { padding: 0 !important; }
    
    .logo-side { display: flex; align-items: center; justify-content: flex-start; padding-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---

if st.session_state.pagina == "Início":
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    
    # --- TÍTULO ATUALIZADO ---
    st.markdown("<h3 style='text-align: center; margin-bottom: 15px; color: white; font-weight: 800;'>ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)

    # 1. ANIVERSARIANTES
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv = []
        for _, r in df_n.iterrows():
            try:
                d_n = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if hoje_br <= d_n <= (hoje_br + timedelta(days=7)): aniv.append(r)
            except: continue
        
        if aniv:
            cn1, cn2, _extra = st.columns([1.5, 1.5, 2])
            with cn1:
                st.markdown(f'<div class="niver-left"><div class="card-niver"><div class="niver-nome">🎈 {aniv[0]["nome"].split()[0]}</div><div class="niver-data">{int(aniv[0]["dia"]):02d}/{int(aniv[0]["mes"]):02d}</div></div></div>', unsafe_allow_html=True)
            with cn2:
                if len(aniv) > 1:
                    st.markdown(f'<div class="niver-right"><div class="card-niver"><div class="niver-nome">🎈 {aniv[1]["nome"].split()[0]}</div><div class="niver-data">{int(aniv[1]["dia"]):02d}/{int(aniv[1]["mes"]):02d}</div></div></div>', unsafe_allow_html=True)

    # 2. MENU + LOGO (Logo aumentado)
    c_menu1, c_menu2, c_logo_img = st.columns([1.5, 1.5, 2])

    with c_menu1:
        st.markdown('<div class="btn-left btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-left btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-left btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniv.", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c_menu2:
        st.markdown('<div class="btn-right btn-2">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-right btn-4">', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-right btn-6">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c_logo_img:
        st.markdown('<div class="logo-side">', unsafe_allow_html=True)
        if os.path.exists("logo igreja.png"):
            # --- LOGO AUMENTADO PARA 150px ---
            st.image("logo igreja.png", width=150) 
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
