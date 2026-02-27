import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
    .card-isosed { background: rgba(255, 215, 0, 0.08) !important; border: 1px solid #ffd700 !important; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .card-aniv { background: rgba(255, 215, 0, 0.2) !important; border: 2px solid #ffd700 !important; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: center; color: #ffd700 !important; }
    .stButton>button { width: 100% !important; background-color: #0f3460 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E LIMPEZA ---
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

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline."

# =========================================================
# --- 3. PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia_row = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia_row.empty: prox_ceia = ceia_row.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.2em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes (Próximos 5)
    st.markdown("<p style='text-align:center; font-weight:bold;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        n_mes = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[n_mes].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
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
# --- 4. PÁGINA: DEVOCIONAL (SISTEMA DE MURAL) ---
# =========================================================
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    df_dev = carregar_dados("Devocional")
    if not df_dev.empty:
        item = df_dev.iloc[-1] # Pega o último cadastrado
        st.markdown(f"<div class='card-isosed'><h3>{item['titulo']}</h3><p>✨ Tema: {item['tema']}</p></div>", unsafe_allow_html=True)
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}")
            st.write(f"**Desafio:** {item['desafio']}")
    else: st.info("Nenhum devocional postado.")

# =========================================================
# --- 5. PÁGINA: GESTÃO (PAINEL DO LÍDER) ---
# =========================================================
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("admin_login"):
            pw = st.text_input("Senha do Painel:", type="password")
            if st.form_submit_button("Entrar"):
                if pw == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta!")
    else:
        st.success("Bem-vindo ao Painel de Gestão")
        t1, t2 = st.tabs(["📊 Estatísticas", "🤖 Gerar Escalas"])
        with t1:
            df_u = carregar_dados("Usuarios")
            st.metric("Total de Membros Cadastrados", len(df_u))
            st.dataframe(df_u, use_container_width=True)
        with t2:
            st.info("Aqui você poderá gerar os rodízios automáticos conforme as regras da igreja.")

# =========================================================
# --- 6. PÁGINA: LEITURA (CADASTRO E PROGRESSO) ---
# =========================================================
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        t_log, t_cad = st.tabs(["Entrar", "Criar Conta"])
        with t_log:
            with st.form("l"):
                tel = st.text_input("WhatsApp:")
                s_pw = st.text_input("Senha:", type="password")
                if st.form_submit_button("Acessar"):
                    df_users = carregar_dados("Usuarios")
                    u = df_users[(df_users['telefone'].astype(str) == str(tel)) & (df_users['senha'].astype(str) == str(s_pw))]
                    if not u.empty:
                        st.session_state.user = u.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Erro no login.")
        with t_cad:
            with st.form("c"):
                c_nom = st.text_input("Nome:")
                c_tel = st.text_input("WhatsApp:")
                c_min = st.text_input("Ministério:")
                c_nas = st.text_input("Nascimento (DD/MM/AAAA):")
                c_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Cadastrar"):
                    sh = conectar_planilha()
                    sh.worksheet("Usuarios").append_row([c_nom, c_tel, c_min, c_nas, c_sen, 1, "Anual 2026"])
                    sh.worksheet("Progresso").append_row([c_tel, "Anual 2026", 1])
                    st.success("Conta criada! Faça o login.")
    else:
        # Progresso da Leitura
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        dia = int(df_p[df_p['usuario'].astype(str) == str(u['telefone'])].iloc[0]['dia_atual'])
        st.markdown(f"### Olá, {u['nome']}! Você está no **Dia {dia}**")
        
        df_lei = carregar_dados("Leitura")
        l = df_lei[df_lei['dia'].astype(str) == str(dia)]
        if not l.empty:
            l = l.iloc[0]
            st.info(f"📍 Referência: {l['referência']}")
            st.markdown(f'<div style="color:#ffd700; font-style:italic;">{buscar_versiculo(l["referência"])}</div>', unsafe_allow_html=True)
            if st.button("✅ Concluir Dia"):
                sh = conectar_planilha()
                aba = sh.worksheet("Progresso")
                cell = aba.find(str(u['telefone']))
                aba.update_cell(cell.row, 3, dia + 1)
                st.rerun()

# --- 7. PÁGINA: ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df_esc = carregar_dados("Escalas")
    t_f, t_o, t_r = st.tabs(["📸 Foto", "🔊 Som", "🤝 Recepção"])
    if not df_esc.empty:
        for t, dep in zip([t_f, t_o, t_r], ["Fotografia", "Mídia", "Recepção"]):
            with t:
                f = df_esc[df_esc['departamento'].str.contains(dep, case=False, na=False)]
                for _, r in f.iterrows():
                    st.markdown(f'<div class="card-isosed"><b>{r["data"]}</b> - {r["responsável"]}</div>', unsafe_allow_html=True)

# (Páginas Agenda e Aniv seguem o mesmo padrão de abas por meses)
