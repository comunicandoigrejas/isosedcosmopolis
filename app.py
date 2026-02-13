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

# --- 4. ESTILO CSS (Simetria Total: Cards e Botões 140x60) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .central-wrapper { max-width: 610px; margin: 0 auto; }

    /* PADRONIZAÇÃO: TUDO COM 140x60 */
    div.stButton > button, .card-niver {
        width: 140px !important; 
        height: 60px !important; 
        border-radius: 15px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        margin-bottom: 8px !important;
    }

    /* Estilo dos Botões */
    div.stButton > button {
        font-size: 13px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }

    /* Estilo dos Cards de Aniversário (Mesmo tamanho do botão) */
    .card-niver {
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        padding: 5px !important;
    }

    /* Alinhamento para o Centro (Aproximação) */
    .align-left { display: flex; justify-content: flex-end; padding-right: 5px; }
    .align-right { display: flex; justify-content: flex-start; padding-left: 5px; }

    /* Forçar alinhamento dos botões Streamlit */
    .btn-left div.stButton > button { margin-left: auto !important; margin-right: 0 !important; }
    .btn-right div.stButton > button { margin-right: auto !important; margin-left: 0 !important; }

    /* Cores dos Botões */
    .btn-1 button { background-color: #0984e3 !important; } .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; } .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; } .btn-6 button { background-color: #ff7675 !important; }

    /* Fontes dos Cards (Ajustadas para 60px de altura) */
    .niver-nome { font-size: 0.9em !important; font-weight: 900 !important; color: #ffd700 !important; text-transform: uppercase; line-height: 1; text-align: center; }
    .niver-data { font-size: 0.75em !important; opacity: 0.9; margin-top: 2px; }

    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>ISOSED</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; opacity: 0.7; font-size: 0.9em;'>✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_nome[hoje_br.month]}</p>", unsafe_allow_html=True)

    _, centro, _ = st.columns([1, 8, 1]) 
    
    with centro:
        st.markdown('<div class="central-wrapper">', unsafe_allow_html=True)
        
        # --- CABEÇALHO DE ANIVERSARIANTES ---
        df_n = carregar_dados("Aniversariantes")
        if not df_n.empty:
            aniv = []
            for _, r in df_n.iterrows():
                try:
                    d_n = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                    if hoje_br <= d_n <= (hoje_br + timedelta(days=7)): aniv.append(r)
                except: continue
            
            if aniv:
                # Mostra os aniversariantes em formato de "botões" no topo
                for i in range(0, len(aniv), 2):
                    c_n1, c_n2 = st.columns(2)
                    par = aniv[i:i+2]
                    with c_n1:
                        if len(par) > 0:
                            st.markdown(f'<div class="align-left"><div class="card-niver"><div class="niver-nome">🎈 {par[0]["nome"].split()[0]}</div><div class="niver-data">{int(par[0]["dia"]):02d}/{int(par[0]["mes"]):02d}</div></div></div>', unsafe_allow_html=True)
                    with c_n2:
                        if len(par) > 1:
                            st.markdown(f'<div class="align-right"><div class="card-niver"><div class="niver-nome">🎈 {par[1]["nome"].split()[0]}</div><div class="niver-data">{int(par[1]["dia"]):02d}/{int(par[1]["mes"]):02d}</div></div></div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 15px;'></div>", unsafe_allow_html=True)

        # --- MENU DE BOTÕES ---
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-left btn-1">', unsafe_allow_html=True)
            st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
            st.markdown('</div><div class="btn-left btn-3">', unsafe_allow_html=True)
            st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
            st.markdown('</div><div class="btn-left btn-5">', unsafe_allow_html=True)
            st.button("🎂 Aniv.", on_click=navegar, args=("Aniversariantes",))
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-right btn-2">', unsafe_allow_html=True)
            st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
            st.markdown('</div><div class="btn-right btn-4">', unsafe_allow_html=True)
            st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
            st.markdown('</div><div class="btn-right btn-6">', unsafe_allow_html=True)
            st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
