import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import requests

# --- 1. CONFIGURAÇÕES E MEMÓRIA ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

# --- FUNÇÃO PARA BUSCAR VERSÍCULO (API DA BÍBLIA) ---
def buscar_versiculo(referencia):
    try:
        url = f"https://bible-api.com/{referencia}?translation=almeida"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['text']
        return "Versículo não encontrado ou referência inválida."
    except:
        return "Erro ao conectar com a API da Bíblia."

# --- 2. CONEXÃO MESTRA ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # Substitua pelo seu ID real entre as aspas
        ID_PLANILHA = "1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0"
        return client.open_by_key(ID_PLANILHA)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            return pd.DataFrame(aba.get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

# --- 3. ESTILO VISUAL MOBILE-FIRST ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; font-weight: 800; }
    .card-isosed {
        background: rgba(255, 215, 0, 0.08) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 15px; padding: 15px; margin-bottom: 15px;
    }
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 12px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3.8em;
    }
    .texto-biblico {
        font-style: italic; color: #cccccc; border-left: 3px solid #ffd700; padding-left: 10px; margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# --- 4. ROTEADOR DE PÁGINAS ---
# =========================================================

# --- PÁGINA: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # 🍇 Santa Ceia Dinâmica (Busca na Agenda)
    df_ag = carregar_dados("Agenda")
    data_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)]
        prox = ceia[ceia['dt'].dt.date >= hoje_br].sort_values('dt').head(1)
        if not prox.empty: data_ceia = prox['data'].values[0]

    st.markdown(f"""
        <div class="card-isosed" style="text-align: center;">
            <h4 style="margin:0; color:#ffd700;">🍇 Próxima Santa Ceia</h4>
            <p style="margin:5px 0; font-size:1.2em;"><b>{data_ceia} às 18h00</b></p>
        </div>
    """, unsafe_allow_html=True)

    # 🎂 Aniversariantes do Mês
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        col_m = 'Mes' if 'Mes' in df_niver.columns else 'Mês'
        niver_mes = df_niver[df_niver[col_m] == hoje_br.month]
        if not niver_mes.empty:
            texto = ", ".join([f"{r['Nome']} ({r['Dia']})" for _, r in niver_mes.sort_values('Dia').iterrows()])
            st.markdown(f"<p style='text-align:center; font-size:0.9em;'>🎂 <b>Niver do Mês:</b> {texto}</p>", unsafe_allow_html=True)

    # Menu
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

# --- PÁGINA: LEITURA (Com API da Bíblia) ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📜 Plano de Leitura</h2>", unsafe_allow_html=True)
    
    df_lei = carregar_dados("Leitura")
    if not df_lei.empty:
        # Exibe a última entrada ou a do dia atual
        item = df_lei.iloc[-1]
        st.markdown(f"### {item['Plano']} - Dia {item['Dia']}")
        st.info(f"📍 **Referência:** {item['Referência']}")
        
        # Chamada da API
        texto_biblico = buscar_versiculo(item['Referência'])
        st.markdown(f'<div class="texto-biblico">{texto_biblico}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"**Resumo para meditação:**\n\n{item['Resumo para meditação']}")
    else: st.info("Plano de leitura não carregado.")

# --- PÁGINA: DEVOCIONAL (Antiga Meditar) ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    
    df_dev = carregar_dados("Devocional")
    if not df_dev.empty:
        item = df_dev.iloc[-1] # Pega o devocional mais recente
        st.markdown(f"### {item['titulo']}")
        st.markdown(f"<p style='text-align:center;'>✨ Tema: {item['tema']} | 📅 {item['data']}</p>", unsafe_allow_html=True)
        
        st.success(f"📖 **Versículo:** {item['versiculo']}")
        st.write(f"**Palavra:**\n\n{item['texto']}")
        
        with st.expander("🎯 Aplicação Pessoal"):
            st.write(item['aplicacao'])
        
        with st.expander("🔥 Desafio do Dia"):
            st.write(item['desafio'])
    else: st.info("Nenhum devocional postado hoje.")

# --- PÁGINA: ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt'] = pd.to_datetime(df_e['Data'], dayfirst=True, errors='coerce')
        for _, r in df_e[df_e['dt'].dt.date >= hoje_br].sort_values('dt').iterrows():
            st.markdown(f'<div class="card-isosed"><b style="color:#ffd700;">{r["Data"]} ({r["Dia"]})</b><br>'
                        f'<b>{r["Evento"]}</b>: {r["Responsável"]}<br>'
                        f'<small>{r["Departamento"]} | {r["Horário"]}</small></div>', unsafe_allow_html=True)
