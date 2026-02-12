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

# Tradução para exibição na Home
meses_pt = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
            7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. FUNÇÕES DE CONEXÃO ---

def buscar_aniversariantes_google():
    try:
        # Puxa as credenciais dos Secrets para evitar erro de TOML
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('calendar', 'v3', credentials=creds)

        # Define intervalo: de hoje até daqui a 7 dias
        t_min = agora_br.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'
        t_max = (agora_br + timedelta(days=7)).isoformat() + 'Z'

        # Busca eventos (ID 'primary' ou o ID da sua agenda de aniversários)
        events_result = service.events().list(
            calendarId='primary', timeMin=t_min, timeMax=t_max,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except:
        return []

def carregar_dados_planilha(aba):
    try:
        # Substitua pelo ID fixo da sua planilha nos Secrets para maior segurança
        url_planilha = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url_planilha)
        if match:
            url = f"https://docs.google.com/spreadsheets/d/{match.group(1)}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. ESTILO CSS (Simetria Total) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 40px !important;
        color: white !important; font-size: 18px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 20px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    .card-niver {
        background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700;
        padding: 15px; border-radius: 20px; text-align: center; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

# --- 5. LOGICA DA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=100)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        dia_n = dias_pt[hoje_br.strftime('%A')]
        st.write(f"✨ {dia_n}, {hoje_br.day} de {meses_pt[hoje_br.month]}")

    # SEÇÃO REAL DE ANIVERSARIANTES
    st.markdown("### 🎂 Aniversariantes da Semana")
    eventos = buscar_aniversariantes_google()
    
    if eventos:
        cols = st.columns(len(eventos) if len(eventos) < 3 else 3)
        for i, ev in enumerate(eventos):
            with cols[i % 3]:
                # Extrai a data do evento
                data_iso = ev['start'].get('date', ev['start'].get('dateTime'))[:10]
                data_br = datetime.strptime(data_iso, '%Y-%m-%d').strftime('%d/%m')
                st.markdown(f"""
                <div class="card-niver">
                    <span style="font-size: 25px;">🎈</span><br>
                    <b>{ev['summary']}</b><br>
                    <span style="color: #ffd700;">{data_br}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

# (Abaixo seguem as abas Agenda, Escalas, Departamentos e Devocional já corrigidas anteriormente)
# ... [O restante do código permanece igual às versões anteriores]
