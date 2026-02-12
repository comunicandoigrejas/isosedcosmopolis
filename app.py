import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pandas as pd
import os

# --- CONFIGURAÇÃO DA API DO CALENDÁRIO ---
# No Streamlit Cloud, você colocaria essas infos em st.secrets
def get_calendar_service():
    # Caminho para o seu arquivo de credenciais JSON
    SERVICE_ACCOUNT_FILE = 'suas-credenciais.json' 
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', creds=creds)

def buscar_aniversariantes():
    try:
        service = get_calendar_service()
        agora = datetime.utcnow().isoformat() + 'Z'
        uma_semana = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
        
        # 'primary' ou o ID da agenda específica de aniversários
        events_result = service.events().list(
            calendarId='primary', timeMin=agora, timeMax=uma_semana,
            singleEvents=True, orderBy='startTime').execute()
        
        return events_result.get('items', [])
    except:
        return []

# --- INTERFACE NA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ... (Cabeçalho com Logo e Título que já criamos)

    # --- SEÇÃO DE ANIVERSARIANTES ---
    st.markdown("### 🎂 Aniversariantes da Semana")
    eventos = buscar_aniversariantes()
    
    if eventos:
        cols = st.columns(len(eventos) if len(eventos) < 3 else 3)
        for idx, evento in enumerate(eventos):
            with cols[idx % 3]:
                # Pega a data e formata
                data_iso = evento['start'].get('dateTime', evento['start'].get('date'))
                data_obj = datetime.strptime(data_iso[:10], '%Y-%m-%d')
                data_br = data_obj.strftime('%d/%m')
                
                st.markdown(f"""
                <div style="background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; 
                            padding: 10px; border-radius: 15px; text-align: center;">
                    <span style="font-size: 20px;">🎈</span><br>
                    <b>{evento['summary']}</b><br>
                    <span style="color: #ffd700;">{data_br}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Nenhum aniversariante nesta semana.")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BOTÕES DO MENU (Mantendo a simetria milimétrica) ---
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)
