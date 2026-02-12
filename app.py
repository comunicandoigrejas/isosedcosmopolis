import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- 1. CONFIGURAÇÃO E CONEXÃO ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# Função para o Calendário do Google (Aniversariantes)
def buscar_aniversariantes():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('calendar', 'v3', credentials=creds)

        agora = datetime.utcnow().isoformat() + 'Z'
        em_uma_semana = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'

        # Busca na agenda (use 'primary' ou o ID da agenda de aniversários)
        events_result = service.events().list(
            calendarId='primary', timeMin=agora, timeMax=em_uma_semana,
            singleEvents=True, orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except:
        return []

# Função para Google Sheets (Escalas e Devocional)
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_PLANILHA"
def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            url = f"https://docs.google.com/spreadsheets/d/{match.group(1)}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 2. ESTILO CSS (Simetria e Design) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 40px !important;
        color: white !important; font-size: 18px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 20px !important;
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

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([1, 3])
    with col_l:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=100)
    with col_r:
        st.title("ISOSED Cosmópolis")
        st.write("Bem-vindo à nossa casa!")

    # SEÇÃO ANIVERSARIANTES
    st.markdown("### 🎂 Aniversariantes da Semana")
    eventos = buscar_aniversariantes()
    if eventos:
        cols = st.columns(len(eventos) if len(eventos) < 3 else 3)
        for i, ev in enumerate(eventos):
            with cols[i % 3]:
                data_iso = ev['start'].get('date', ev['start'].get('dateTime'))[:10]
                data_br = datetime.strptime(data_iso, '%Y-%m-%d').strftime('%d/%m')
                st.markdown(f'<div class="card-niver">🎈 <b>{ev["summary"]}</b><br><span style="color:#ffd700">{data_br}</span></div>', unsafe_allow_html=True)
    else:
        st.info("Nenhum aniversariante nos próximos dias. 🙏")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditação Diária")
    data_sel = st.date_input("Selecione o dia:", format="DD/MM/YYYY")
    data_str = data_sel.strftime('%d/%m/%Y')
    
    df = carregar_dados("Devocional")
    if not df.empty:
        df["data"] = df["data"].astype(str).str.strip()
        hoje = df[df["data"] == data_str]
        if not hoje.empty:
            dev = hoje.iloc[0]
            st.markdown("---")
            st.header(f"✨ {dev.get('titulo','')}")
            st.success(f"📖 **Versículo:** {dev.get('versiculo','')}")
            st.write(dev.get("texto",""))
        else: st.info(f"📅 Sem devocional para {data_str}.")
    else: st.error("Erro ao carregar a aba 'Devocional'.")

# (Demais páginas Agenda, Escalas e Departamentos seguem a lógica anterior)
