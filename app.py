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

# CSS PARA FORÇAR BRANCO E FORMATAR CARDS
st.markdown("""
    <style>
    /* Fundo e Texto Global */
    [data-testid="stAppViewContainer"], .main, .stApp {
        background-color: #1a1a2e !important;
        color: white !important;
    }
    
    /* Forçar Branco em todas as fontes */
    p, span, div, label, h1, h2, h3, .stMarkdown {
        color: white !important;
    }
    
    /* Títulos em Amarelo para destaque */
    h1, h2, h3, b, strong {
        color: #ffd700 !important;
        text-align: center;
    }

    /* Cards de Escala Menores */
    .card-isosed {
        background: rgba(255, 215, 0, 0.05) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 8px; padding: 10px; margin-bottom: 8px;
        color: white !important;
    }
    
    /* Cards de Aniversário (Página Inicial) */
    .card-aniv {
        background: rgba(255, 215, 0, 0.2) !important;
        border: 1px solid #ffd700 !important;
        border-radius: 10px; padding: 8px; margin-bottom: 5px;
        text-align: center; font-weight: bold; color: white !important;
    }

    /* Botões */
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 10px !important;
        font-weight: bold; border: 1px solid #ffd700; height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO E DADOS ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
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
        except: return pd.DataFrame()
    return pd.DataFrame()

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline."

def obter_datas_culto_pt(ano, mes):
    dias_pt = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    cal = calendar.Calendar()
    dias_mes = [d for sem in cal.monthdatescalendar(ano, mes) for d in sem if d.month == mes]
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

# =========================================================
# --- ROTEADOR DE PÁGINAS (ESTRUTURA INDEPENDENTE) ---
# =========================================================

# 1. PÁGINA INICIAL
if st.session_state.pagina == "Início":
    # LOGO
    c_l1, c_l2, c_l3 = st.columns([1, 1.2, 1])
    with c_l2:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Próxima Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox_ceia = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes
    st.markdown("<h3>🎂 PRÓXIMOS ANIVERSARIANTES</h3>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        n_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in n_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

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

# 2. ESCALAS
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
            o = prox[prox['departamento'].str.contains("Mídia|Som|Operador", case=False, na=False)]
            for _, r in o.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t3:
            rec = prox[prox['departamento'].str.contains("Recepção", case=False, na=False)]
            for _, r in rec.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
    else: st.info("Escalas não encontradas.")

# 3. AGENDA E ANIVERSÁRIOS
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Agenda")
    abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                for _, r in m_df.iterrows(): st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")

elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Aniversariantes")
    abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    if not df.empty:
        c_m = next((c for c in df.columns if 'mes' in c or 'mês' in c), 'mes')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df[c_m].astype(int) == (i+1)].sort_values('dia')
                for _, r in m_df.iterrows(): st.write(f"🎁 Dia {r['dia']} - {r['nome']}")

# 4. GESTÃO
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("adm"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Liberar"):
                if pw == "ISOSED2026": st.session_state.admin_ok = True; st.rerun()
    else:
        st.success("Painel do Líder Ativado")
        m = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        tp = st.selectbox("Tipo:", ["Fotografia", "Recepção", "Som/Mídia"])
        if st.button("Gerar Escala agora"):
            datas = obter_datas_culto_pt(2026, m)
            sh = conectar_planilha()
            aba = sh.worksheet("Escalas")
            for d in datas:
                h = "18:00" if d['is_domingo'] else "19:30"
                aba.append_row([d['data'], d['dia_pt'], h, "Culto", tp, "A definir"])
            st.success("Datas geradas na planilha!")

# 5. DEVOCIONAL
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Devocional")
    if not df.empty:
        i = df.iloc[-1]
        st.markdown(f"### {i['titulo']}")
        st.write(i['texto'])

# 6. LEITURA
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        with st.form("login"):
            tel = st.text_input("WhatsApp:"); sen = st.text_input("Senha:", type="password")
            if st.form_submit_button("Entrar"):
                df_u = carregar_dados("Usuarios")
                u_f = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                if not u_f.empty: st.session_state.user = u_f.iloc[0].to_dict(); st.rerun()
    else:
        st.write(f"Olá, {st.session_state.user['nome']}! Bem-vindo ao plano.")
