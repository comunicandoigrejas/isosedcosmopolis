import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- 1. CONFIGURAÇÃO DE FUSO E DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
            7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. FUNÇÕES DE CONEXÃO ---

def get_calendar_service():
    if "gcp_service_account" not in st.secrets:
        return None
    creds_info = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(creds_info)
    return build('calendar', 'v3', credentials=creds)

def buscar_aniversariantes_semana():
    try:
        service = get_calendar_service()
        if not service: return []
        t_min = agora_br.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        t_max = (agora_br + timedelta(days=7)).isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=t_min, timeMax=t_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except: return []

def buscar_aniversariantes_ano():
    try:
        service = get_calendar_service()
        if not service: return []
        # Busca do início ao fim do ano atual
        t_min = datetime(agora_br.year, 1, 1).isoformat() + 'Z'
        t_max = datetime(agora_br.year, 12, 31).isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary', timeMin=t_min, timeMax=t_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except: return []

def carregar_dados(aba):
    try:
        url_planilha = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url_planilha)
        if match:
            url = f"https://docs.google.com/spreadsheets/d/{match.group(1)}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria para 5 botões) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    div.stButton > button {
        width: 100% !important; height: 65px !important; border-radius: 40px !important;
        color: white !important; font-size: 16px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 15px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }
    div.stButton:nth-of-type(5) > button { background-color: #fdcb6e !important; }
    
    .btn-voltar div.stButton > button { background-color: rgba(255,255,255,0.1) !important; height: 50px !important; }
    .card-niver { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; padding: 15px; border-radius: 20px; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DAS PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=90)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write(f"✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_pt[hoje_br.month]}")

    st.markdown("### 🎂 Aniversariantes da Semana")
    eventos = buscar_aniversariantes_semana()
    if eventos:
        cols = st.columns(min(len(eventos), 3))
        for i, ev in enumerate(eventos):
            with cols[i % 3]:
                data_iso = ev['start'].get('date', ev['start'].get('dateTime'))[:10]
                data_br = datetime.strptime(data_iso, '%Y-%m-%d').strftime('%d/%m')
                st.markdown(f'<div class="card-niver">🎈 <b>{ev["summary"]}</b><br>{data_br}</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum aniversariante nos próximos dias.")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.button("🎂 ANIVERSARIANTES", on_click=navegar, args=("Aniversariantes",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Aniversariantes":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🎂 Aniversariantes do Ano")
    
    eventos_ano = buscar_aniversariantes_ano()
    if eventos_ano:
        # Agrupar por mês
        por_mes = {m: [] for m in range(1, 13)}
        for ev in eventos_ano:
            data_iso = ev['start'].get('date', ev['start'].get('dateTime'))[:10]
            dt = datetime.strptime(data_iso, '%Y-%m-%d')
            por_mes[dt.month].append({"nome": ev['summary'], "dia": dt.day})
        
        # Exibir por mês
        for m_num in range(1, 13):
            if por_mes[m_num]:
                with st.expander(f"📅 {meses_pt[m_num]}", expanded=(m_num == hoje_br.month)):
                    # Ordenar por dia
                    aniv_ordenados = sorted(por_mes[m_num], key=lambda x: x['dia'])
                    for a in aniv_ordenados:
                        st.write(f"🎁 **Dia {a['dia']:02d}:** {a['nome']}")
    else:
        st.warning("Não foi possível carregar a lista de aniversariantes.")

# [As outras abas Agenda, Escalas, Departamentos e Devocional permanecem conforme as versões anteriores]
