import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE FUSO E DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=387999147#gid=387999147"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e') for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILO CSS (Focado em manter as duplas compactas) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    
    div.stButton > button {
        width: 100% !important; height: 60px !important; border-radius: 40px !important;
        color: white !important; font-size: 16px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 12px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
    }
    
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }
    div.stButton:nth-of-type(5) > button { background-color: #fdcb6e !important; }
    
    /* QUADRO AMARELO COMPACTO */
    .card-niver { 
        background: rgba(255, 215, 0, 0.1); 
        border: 1px solid #ffd700; 
        padding: 5px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 10px;
        font-size: 0.85em;
        width: 100%; /* Ocupa a coluna */
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGICA DA PÁGINA INICIAL ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=80)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        dia_semana = dias_pt[hoje_br.strftime('%A')]
        st.write(f"✨ {dia_semana}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    st.markdown("<h3 style='text-align: center;'>🎂 Aniversariantes da Semana</h3>", unsafe_allow_html=True)
    
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        aniv_semana = []
        for _, r in df_niver.iterrows():
            try:
                d_niver = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if hoje_br <= d_niver <= (hoje_br + timedelta(days=7)):
                    aniv_semana.append(r)
            except: continue
        
        if aniv_semana:
            # CENTRALIZADOR: Cria 3 colunas e usa a do meio (maior) para os cards
            _, centro, _ = st.columns([1, 3, 1])
            with centro:
                # Divide a lista em pares (2 em 2)
                for i in range(0, len(aniv_semana), 2):
                    par = aniv_semana[i:i+2]
                    cols = st.columns(2) # Cria a dupla
                    for idx, pessoa in enumerate(par):
                        with cols[idx]:
                            st.markdown(f'<div class="card-niver">🎈 <b>{pessoa["nome"]}</b><br>{int(pessoa["dia"]):02d}/{int(pessoa["mes"]):02d}</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")
    
    # BOTÕES PRINCIPAIS
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.button("🎂 ANIVERSARIANTES", on_click=navegar, args=("Aniversariantes",))
    st.markdown('</div>', unsafe_allow_html=True)

# (O restante do código das outras abas permanece o mesmo)
