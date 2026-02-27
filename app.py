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

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    
    /* QUADROS DE ESCALA (Compactos) */
    .card-isosed {
        background: rgba(255, 215, 0, 0.08) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 8px; 
        padding: 8px 12px; 
        margin-bottom: 8px;
        font-size: 0.85em; /* Fonte menor */
    }
    
    /* QUADROS DE ANIVERSARIANTES (Página Inicial) */
    .card-aniv {
        background: rgba(255, 215, 0, 0.2) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 10px; padding: 8px; margin-bottom: 6px;
        text-align: center; color: #ffd700 !important; font-weight: bold;
        font-size: 0.9em;
    }
    
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 10px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3.5em;
    }
    
    h1, h2, h3 { color: #ffd700 !important; text-align: center; margin-top: 0; }
    .texto-biblico { font-style: italic; color: #ffd700; border-left: 3px solid #ffd700; padding-left: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E DADOS ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
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

def atualizar_contador():
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Acessos")
        valor = int(aba.acell('A2').value or 0) + 1
        aba.update_acell('A2', valor)
        return valor
    except: return "---"

# =========================================================
# --- PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    # EXIBIÇÃO DO LOGO NO TOPO
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # Santa Ceia Dinâmica
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox_ceia = ceia.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes do Mês (Destaque Amarelo Compacto)
    st.markdown("<p style='text-align:center; font-weight:bold; margin-bottom:5px;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        # Tenta achar a coluna de mês (com ou sem acento)
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in niver_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    # Menu
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

    # Rodapé com Redes Sociais e Contador
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><a href="https://instagram.com/isosedcosmopolis" style="color:#ffd700; text-decoration:none; margin:0 10px;">📸 Instagram</a> | <a href="https://youtube.com/@isosedcosmopolis" style="color:#ffd700; text-decoration:none; margin:0 10px;">🎥 YouTube</a></div>', unsafe_allow_html=True)
    
    if 'visitas' not in st.session_state: st.session_state.visitas = atualizar_contador()
    st.markdown(f"<p style='text-align:center; opacity:0.4; font-size:0.7em;'>Visitante nº: {st.session_state.visitas} | ISOSED 2026</p>", unsafe_allow_html=True)

# =========================================================
# --- PÁGINA: ESCALAS (Cards Menores e Dia da Semana) ---
# =========================================================
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt'] = pd.to_datetime(df_e['data'], dayfirst=True, errors='coerce')
        # Filtra datas de hoje em diante
        prox = df_e[df_e['dt'].dt.date >= hoje_br].sort_values('dt')
        
        t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som/Mídia", "🤝 Recepção"])
        
        with t1:
            f_df = prox[prox['departamento'].str.contains("Foto", case=False, na=False)]
            for _, r in f_df.iterrows():
                st.markdown(f"""
                    <div class="card-isosed">
                        <b>{r['data']} - {r['dia']}</b><br>
                        👤 {r['responsável']}
                    </div>
                """, unsafe_allow_html=True)
        
        with t2:
            o_df = prox[prox['departamento'].str.contains("Mídia|Som|Operador", case=False, na=False)]
            for _, r in o_df.iterrows():
                st.markdown(f"""
                    <div class="card-isosed">
                        <b>{r['data']} - {r['dia']}</b><br>
                        👤 {r['responsável']}
                    </div>
                """, unsafe_allow_html=True)

        with t3:
            r_df = prox[prox['departamento'].str.contains("Recepção", case=False, na=False)]
            for _, r in r_df.iterrows():
                st.markdown(f"""
                    <div class="card-isosed">
                        <b>{r['data']} - {r['dia']}</b><br>
                        👤 {r['responsável']}
                    </div>
                """, unsafe_allow_html=True)
