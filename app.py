import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Lógica: Domingo desta semana até Segunda da próxima (Janela de 9 dias)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
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

def registrar_leitura_log(nome, data):
    try:
        if "gcp_service_account" not in st.secrets: return False
        creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build('sheets', 'v4', credentials=creds)
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        sheet_id = match.group(1)
        values = [[nome, data]]
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Leitura_Log!A:B",
            valueInputOption="RAW", body=body).execute()
        return True
    except: return False

# --- 3. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state: 
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: 
    st.session_state.usuario = None

def navegar(p): 
    st.session_state.pagina = p

# --- 4. ESTILO CSS (Contraste Máximo e Forçado) ---
st.markdown("""
    <style>
    /* Esconde elementos do Streamlit */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    
    /* Fundo Escuro para Contraste */
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; color: white !important; }

    .main-wrapper { max-width: 550px; margin: 0 auto; padding: 5px; }

    /* ESTILO DOS BOTÕES (Forçando cor da fonte) */
    div.stButton > button {
        width: 140px !important; 
        height: 60px !important; 
        border-radius: 12px !important;
        font-size: 11px !important;
        font-weight: 900 !important; /* Fonte bem grossa */
        text-transform: uppercase !important;
        color: #FFFFFF !important; /* TEXTO BRANCO POR PADRÃO */
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        display: block !important;
    }

    /* WRAPPERS PARA AS CORES (Garante que a cor apareça) */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-orange button { background-color: #e17055 !important; }
    .btn-green button { background-color: #00b894 !important; }
    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-red button { background-color: #ff7675 !important; }
    
    /* Botão de Aniversários: Amarelo com texto PRETO para ler melhor */
    .btn-yellow button { 
        background-color: #f1c40f !important; 
        color: #000000 !important; 
    }

    /* CARDS DE ANIVERSÁRIO */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
        text-align: center !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; padding: 0 5px; }
    .niver-data { font-size: 0.9em !important; font-weight: bold; color: #FFFFFF !important; margin-top: 5px; }
    
    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 25px;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # 1. ANIVERSARIANTES (Domingo a Segunda)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_semana = []
        for _, r in df_n.iterrows():
            try:
                d_aniv = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= d_aniv <= segunda_proxima:
                    aniv_semana.append(r)
            except: 
                continue
        
        if aniv_semana:
            st.markdown("<p style='text-align:center; color:#ffd700; font-weight:bold; font-size:1.1em;'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            cols_aniv = st.columns(len(aniv_semana) if len(aniv_semana) <= 4 else 4)
            for idx, p in enumerate(aniv_semana):
                with cols_aniv[idx % 4]:
                    st.markdown(f"""
                        <div class="card-niver">
                            <div class="niver-nome">{p['nome']}</div>
                            <div class="niver-data">{int(p['dia']):02d}/{int(p['mes']):02d}</div>
                        </div>
                    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MENU + LOGO (Aproximados e Coloridos)
    # A proporção [1.5, 1.5, 2] garante que os botões fiquem juntos à esquerda e o logo à direita
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    
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
        # AQUI ESTAVA O ERRO DE INDENTAÇÃO - AGORA CORRIGIDO:
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c_logo:
        if os.path.exists("logo igreja.png"):
            # Centraliza o logo verticalmente para alinhar com os botões
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.image("logo igreja.png", width=200)

    st.markdown('</div>', unsafe_allow_html=True)
