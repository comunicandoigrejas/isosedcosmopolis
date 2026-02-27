import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import requests
import calendar

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'user' not in st.session_state: st.session_state.user = None
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p): st.session_state.pagina = p

# --- CSS: FUNDO ESCURO, TEXTO BRANCO E CAIXAS DE ENTRADA BRANCAS COM FONTE PRETA ---
st.markdown("""
    <style>
    /* Fundo do App */
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    
    /* Texto Geral em Branco */
    p, span, div, label, .stMarkdown { color: white !important; }
    h1, h2, h3, b, strong { color: #ffd700 !important; text-align: center; }

    /* CAIXAS DE TEXTO: Fundo Branco e Fonte Preta (Para leitura clara) */
    input, textarea, [data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ffd700 !important;
    }
    
    /* Garante que o texto digitado seja preto */
    .stTextInput input { color: black !important; }
    .stSelectbox div[data-baseweb="select"] { color: black !important; }

    /* BOTÕES AZUIS COM FONTE BRANCA */
    div.stButton > button, div.stFormSubmitButton > button {
        width: 100% !important;
        background-color: #0f3460 !important; 
        color: white !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.5em !important;
    }
    
    /* CARDS DE ESCALA (Compactos) */
    .card-isosed { 
        background: rgba(255, 215, 0, 0.05) !important; 
        border: 1px solid #ffd700 !important; 
        border-radius: 8px; padding: 10px; margin-bottom: 8px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E APOIO ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
    except: return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            df.columns = df.columns.str.strip().str.lower()
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

# =========================================================
# --- ROTEADOR PRINCIPAL (TODOS OS ELIF ALINHADOS) ---
# =========================================================

# 1. PÁGINA INICIAL
if st.session_state.pagina == "Início":
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em; color:#ffd700;">{prox} às 18h00</b></div>', unsafe_allow_html=True)

    # Botões
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

# 2. PÁGINA ESCALAS (FIX: REORGANIZADA)
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df_esc = carregar_dados("Escalas")
    if not df_esc.empty:
        df_esc['dt'] = pd.to_datetime(df_esc['data'], dayfirst=True, errors='coerce')
        prox = df_esc[df_esc['dt'].dt.date >= hoje_br].sort_values('dt')
        
        t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som/Mídia", "🤝 Recepção"])
        with t1:
            f = prox[prox['departamento'].str.contains("Foto", case=False, na=False)]
            for _, r in f.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t2:
            o = prox[prox['departamento'].str.contains("Mídia|Som", case=False, na=False)]
            for _, r in o.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t3:
            rec = prox[prox['departamento'].str.contains("Recepção", case=False, na=False)]
            for _, r in rec.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
    else: st.info("Nenhuma escala encontrada.")

# 3. DEVOCIONAL (Puxando todas as informações)
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    df_dev = carregar_dados("Devocional")
    if not df_dev.empty:
        item = df_dev.iloc[-1]
        st.markdown(f"### {item['titulo']}")
        st.write(f"✨ **Tema:** {item['tema']} | 📅 **Data:** {item['data']}")
        st.info(f"📖 **Versículo:** {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}")
            st.write(f"**Desafio:** {item['desafio']}")

# 4. LEITURA (Puxando do Progresso)
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        with st.form("login_leitura"):
            tel = st.text_input("WhatsApp (Login):")
            sen = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar no Plano"):
                df_u = carregar_dados("Usuarios")
                u_f = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                if not u_f.empty:
                    st.session_state.user = u_f.iloc[0].to_dict()
                    st.rerun()
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        p_row = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        if not p_row.empty:
            dia_atual = int(p_row.iloc[0]['dia_atual'])
            st.markdown(f"### Olá, {u['nome']}! Você está no **Dia {dia_atual}**")
            # Aqui você puxaria a leitura do dia da aba "Leitura"
            st.write("Continue sua jornada bíblica hoje!")
