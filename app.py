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
    .card-isosed { background: rgba(255, 215, 0, 0.08) !important; border: 1px solid #ffd700 !important; border-radius: 12px; padding: 10px; margin-bottom: 10px; font-size: 0.9em; }
    .card-aniv { background: rgba(255, 215, 0, 0.2) !important; border: 2px solid #ffd700 !important; border-radius: 10px; padding: 8px; margin-bottom: 6px; text-align: center; color: #ffd700 !important; font-weight: bold; }
    .stButton>button { width: 100% !important; background-color: #0f3460 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO MESTRA ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # VERIFIQUE ESTE ID:
        return client.open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            df.columns = df.columns.str.strip().str.lower()
            return df
        except Exception as e:
            st.warning(f"Aba '{aba_nome}' não encontrada ou sem dados. Erro: {e}")
            return pd.DataFrame()
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
# --- PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    # --- LOGO ---
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)
        else:
            st.warning("⚠️ Arquivo 'logo igreja.png' não encontrado no GitHub.")

    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox_ceia = ceia.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes do Mês
    st.markdown("<p style='text-align:center; font-weight:bold;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in niver_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    # Menu
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

# =========================================================
# --- PÁGINA: ESCALAS (ABAS POR FUNÇÃO) ---
# =========================================================
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        prox = df[df['dt'].dt.date >= hoje_br].sort_values('dt')
        
        t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som/Mídia", "🤝 Recepção"])
        with t1:
            f_df = prox[prox['departamento'].str.contains("Foto", case=False, na=False)]
            for _, r in f_df.iterrows():
                st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t2:
            o_df = prox[prox['departamento'].str.contains("Mídia|Som|Operador", case=False, na=False)]
            for _, r in o_df.iterrows():
                st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t3:
            r_df = prox[prox['departamento'].str.contains("Recepção", case=False, na=False)]
            for _, r in r_df.iterrows():
                st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)

# =========================================================
# --- PÁGINA: GESTÃO (GERADOR DE SOM) ---
# =========================================================
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("adm"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Liberar"):
                if pw == "ISOSED2026": st.session_state.admin_ok = True; st.rerun()
                else: st.error("Incorreto!")
    else:
        m = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        tp = st.selectbox("Tipo:", ["Fotografia", "Recepção", "Som/Mídia"])
        if st.button("Gerar Escala"):
            datas_culto = obter_datas_culto_pt(2026, m)
            sh = conectar_planilha()
            aba = sh.worksheet("Escalas")
            
            if tp == "Som/Mídia":
                pg = ["Lucas", "Samuel", "Nicholas"]
                pdom = ["Júnior", "Lucas", "Samuel", "Nicholas"]
                ig, idom = 0, 0
                for d in datas_culto:
                    hor = "18:00" if d['is_domingo'] else "19:30"
                    resp = pdom[idom % 4] if d['is_domingo'] else pg[ig % 3]
                    if d['is_domingo']: idom += 1
                    else: ig += 1
                    aba.append_row([d['data'], d['dia_pt'], hor, "Culto", "Mídia", resp])
                st.success("✅ Escala de Som Gerada!")

# (Outras abas como Agenda e Aniv seguem o mesmo padrão...)
