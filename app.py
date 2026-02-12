import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- 1. CONFIGURAÇÃO DE FUSO E IDIOMA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Dicionário de tradução manual para garantir PT-BR no calendário e datas
MESES_PT = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
            7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
DIAS_PT = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. FUNÇÕES DE CONEXÃO (ROBUSTAS) ---
def buscar_aniversariantes():
    try:
        creds_info = st.secrets["gcp_service_account"]
        creds = service_account.Credentials.from_service_account_info(creds_info)
        service = build('calendar', 'v3', credentials=creds)
        # Busca aniversários na semana
        t_min = agora_br.isoformat()
        t_max = (agora_br + timedelta(days=7)).isoformat()
        events = service.events().list(calendarId='primary', timeMin=t_min, timeMax=t_max, singleEvents=True).execute()
        return events.get('items', [])
    except: return []

def carregar_dados(aba):
    try:
        # Puxa o ID dos secrets para evitar erros de link
        id_plan = st.secrets["planilha"]["id"]
        url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
        df = pd.read_csv(url)
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro técnico na aba {aba}: {e}")
        return pd.DataFrame()

# --- 3. NAVEGAÇÃO E ESTILO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

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
    }
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. PÁGINAS ---
if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("ISOSED Cosmópolis")
    # Data em Português na Home
    st.write(f"✨ {DIAS_PT[hoje_br.strftime('%A')]}, {hoje_br.day} de {MESES_PT[hoje_br.month]}")

    # Aniversariantes do Google Calendar
    st.markdown("### 🎂 Aniversariantes da Semana")
    niver = buscar_aniversariantes()
    if niver:
        for ev in niver:
            data_niver = datetime.strptime(ev['start'].get('date', ev['start'].get('dateTime'))[:10], '%Y-%m-%d')
            st.markdown(f"🎈 **{ev['summary']}** - {data_niver.strftime('%d/%m')}")
    else: st.info("Nenhum aniversariante nesta semana. 🙏")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditação Diária")
    
    # Calendário (A tradução do widget depende do navegador, mas confirmamos abaixo)
    data_sel = st.date_input("Selecione o dia:", value=hoje_br, format="DD/MM/YYYY")
    st.write(f"📅 Lendo a palavra de: **{data_sel.strftime('%d/%m/%Y')}**")

    df = carregar_dados("Devocional")
    if not df.empty:
        df["data"] = df["data"].astype(str).str.strip()
        hoje = df[df["data"] == data_sel.strftime('%d/%m/%Y')]
        if not hoje.empty:
            dev = hoje.iloc[0]
            st.markdown(f"### {dev.get('titulo', '')}")
            st.caption(f"🏷️ Tema: {dev.get('tema', 'Geral')}")
            st.success(f"📖 **Versículo:** {dev.get('versiculo', '')}")
            st.write(dev.get("texto", ""))
            if pd.notna(dev.get("aplicacao")): st.info(f"💡 **Aplicação:** {dev['aplicacao']}")
            if pd.notna(dev.get("desafio")): st.warning(f"🎯 **Desafio:** {dev['desafio']}")
        else: st.info(f"📅 Sem devocional para {data_sel.strftime('%d/%m/%Y')}.")
    else: st.error("Erro ao carregar aba Devocional.")

# (Demais páginas Agenda, Escalas e Departamentos seguem a mesma lógica)
