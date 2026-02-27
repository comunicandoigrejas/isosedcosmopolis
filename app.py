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

# CSS TOTAL - FORÇANDO BRANCO E BOTÕES AZUIS
st.markdown("""
    <style>
    /* Fundo Global */
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    
    /* Texto Geral em Branco */
    p, span, div, label, .stMarkdown { color: white !important; }
    h1, h2, h3, b, strong { color: #ffd700 !important; text-align: center; }

    /* PADRONIZAÇÃO DE TODOS OS BOTÕES (Azul com Fonte Branca) */
    div.stButton > button, div.stFormSubmitButton > button {
        width: 100% !important;
        background-color: #0f3460 !important; 
        color: white !important; 
        border: 2px solid #ffd700 !important; /* Borda amarela para destaque */
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.5em !important;
        transition: 0.3s;
    }
    
    /* Efeito ao passar o mouse */
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #ffd700 !important;
        color: #1a1a2e !important;
    }

    /* Cards */
    .card-isosed {
        background: rgba(255, 215, 0, 0.05) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 8px; padding: 12px; margin-bottom: 10px;
    }
    .card-aniv {
        background: rgba(255, 215, 0, 0.2) !important;
        border: 1px solid #ffd700 !important;
        border-radius: 10px; padding: 10px; margin-bottom: 6px;
        text-align: center; color: white !important; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE APOIO ---
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

def obter_datas_culto_pt(ano, mes):
    dias_pt = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    cal = calendar.Calendar()
    dias_mes = [d for sem in cal.monthdatescalendar(ano, mes) for d in sem if d.month == mes]
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

# =========================================================
# --- ROTEADOR ---
# =========================================================

if st.session_state.pagina == "Início":
    # Logo
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes
    st.markdown("<h3>🎂 PRÓXIMOS ANIVERSARIANTES</h3>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        n_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in n_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    # Botões de Navegação (Agora todos Azuis)
    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with col_b:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        prox = df[df['dt'].dt.date >= hoje_br].sort_values('dt')
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

elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("adm"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Liberar"):
                if pw == "ISOSED2026": st.session_state.admin_ok = True; st.rerun()
    else:
        m = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        tp = st.selectbox("Setor:", ["Fotografia", "Recepção", "Som/Mídia"])
        if st.form_submit_button(f"Gerar {tp}"): # Agora este botão também será azul
            datas = obter_datas_culto_pt(2026, m)
            sh = conectar_planilha()
            aba = sh.worksheet("Escalas")
            for d in datas:
                h = "18:00" if d['is_domingo'] else "19:30"
                aba.append_row([d['data'], d['dia_pt'], h, "Culto", tp, "A definir"])
            st.success("Escala enviada para a planilha!")
