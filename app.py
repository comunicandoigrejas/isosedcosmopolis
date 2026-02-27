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

# Inicialização de Memória
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'user' not in st.session_state: st.session_state.user = None
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p): st.session_state.pagina = p

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    .card-isosed { background: rgba(255, 215, 0, 0.08) !important; border: 1px solid #ffd700 !important; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .card-aniv { background: rgba(255, 215, 0, 0.2) !important; border: 2px solid #ffd700 !important; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: center; color: #ffd700 !important; font-weight: bold; }
    .stButton>button { width: 100% !important; background-color: #0f3460 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO MESTRA (COM DEBUG) ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Verifica se os segredos existem
        if "gcp_service_account" not in st.secrets:
            st.error("❌ Segredos (Secrets) não configurados no Streamlit Cloud!")
            return None
        
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # --- COLE SEU ID AQUI ---
        ID_PLANILHA = "1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0" 
        
        return client.open_by_key(ID_PLANILHA)
    except Exception as e:
        st.error(f"❌ Erro ao conectar no Google Sheets: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            if df.empty:
                return pd.DataFrame()
            # Limpeza de colunas
            df.columns = df.columns.str.strip().str.lower()
            return df
        except Exception as e:
            st.warning(f"⚠️ Aba '{aba_nome}' não encontrada ou vazia.")
            return pd.DataFrame()
    return pd.DataFrame()

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline."

# =========================================================
# --- ROTEADOR PRINCIPAL (ALINHADO À ESQUERDA) ---
# =========================================================

# --- PÁGINA: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # 🍇 Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty and 'evento' in df_ag.columns:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia_row = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia_row.empty: prox_ceia = ceia_row.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.4em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # 🎂 Aniversariantes (Destaque Amarelo)
    st.markdown("<p style='text-align:center; font-weight:bold;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        if not niver_f.empty:
            for _, r in niver_f.iterrows():
                st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)
        else: st.write("Nenhum aniversariante para os próximos dias.")

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

    # Rodapé
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    fl1, fl2, fl3 = st.columns([1, 1.2, 1])
    with fl2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    st.markdown('<div style="text-align:center;"><a href="https://instagram.com/isosedcosmopolis" style="color:#ffd700; text-decoration:none;">📸 Instagram</a></div>', unsafe_allow_html=True)

# --- PÁGINA: DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    df = carregar_dados("Devocional")
    if not df.empty:
        item = df.iloc[-1]
        st.markdown(f"<div class='card-isosed'><h3>{item['titulo']}</h3><p>✨ Tema: {item['tema']}</p></div>", unsafe_allow_html=True)
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}\n\n**Desafio:** {item['desafio']}")

# --- PÁGINA: GESTÃO ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("a"):
            pw = st.text_input("Senha do Painel:", type="password")
            if st.form_submit_button("Acessar"):
                if pw == "ISOSED2026": 
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Incorreto!")
    else:
        st.success("Painel de Gestão Liberado")
        df_u = carregar_dados("Usuarios")
        st.write(f"Total de membros: {len(df_u)}")
        st.dataframe(df_u)

# --- PÁGINA: LEITURA (LOGIN/CADASTRO) ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        t1, t2 = st.tabs(["Entrar", "Novo Cadastro"])
        with t1:
            with st.form("l"):
                tel = st.text_input("WhatsApp:")
                sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Entrar"):
                    df_u = carregar_dados("Usuarios")
                    u = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                    if not u.empty:
                        st.session_state.user = u.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Dados inválidos.")
        with t2:
            with st.form("c"):
                c_nom = st.text_input("Nome:")
                c_tel = st.text_input("Telefone:")
                c_min = st.text_input("Ministério:")
                c_nas = st.text_input("Nascimento:")
                c_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Cadastrar"):
                    sh = conectar_planilha()
                    sh.worksheet("Usuarios").append_row([c_nom, c_tel, c_min, c_nas, c_sen, 1, "Anual 2026"])
                    sh.worksheet("Progresso").append_row([c_tel, "Anual 2026", 1])
                    st.success("Pronto! Faça login.")
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        dia = int(df_p[df_p['usuario'].astype(str) == str(u['telefone'])].iloc[0]['dia_atual'])
        st.markdown(f"### Olá, {u['nome']}! Dia {dia}")
        df_l = carregar_dados("Leitura")
        l = df_l[df_l['dia'].astype(str) == str(dia)]
        if not l.empty:
            l = l.iloc[0]
            st.info(f"📍 {l['referência']}")
            st.write(buscar_versiculo(l['referência']))
            if st.button("✅ Concluir Dia"):
                sh = conectar_planilha()
                aba = sh.worksheet("Progresso")
                cell = aba.find(str(u['telefone']))
                aba.update_cell(cell.row, 3, dia + 1)
                st.rerun()

# --- PÁGINA: ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Escalas")
    t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som", "🤝 Recepção"])
    if not df.empty:
        for t, dep in zip([t1, t2, t3], ["Foto", "Mídia", "Recepção"]):
            with t:
                f = df[df['departamento'].str.contains(dep, case=False, na=False)]
                for _, r in f.iterrows():
                    st.markdown(f'<div class="card-isosed"><b>{r["data"]}</b> - {r["responsável"]}</div>', unsafe_allow_html=True)
