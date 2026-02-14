import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Janela de Aniversários: Domingo a Segunda
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (Session State) ---
# Isso evita o erro de AttributeError
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p

# --- 3. FUNÇÕES GLOBAIS (Devem ficar fora do if/elif) ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normalização de nomes de colunas
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(URL_PLANILHA)
    except Exception as e:
        st.error(f"Erro de conexão API: {e}")
        return None

def salvar_novo_usuario(lista_dados):
    try:
        sh = conectar_planilha()
        if sh:
            aba = sh.worksheet("Usuarios") 
            aba.append_row(lista_dados)
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao gravar na planilha: {e}")
        return False

# --- 4. ESTILO CSS ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; font-weight: 800 !important; }
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important; height: 65px !important;
        background-color: #0a3d62 !important; border-radius: 12px !important;
        border: 2px solid #3c6382 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }
    button[data-testid="stBaseButton-secondary"] p { color: #FFFFFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
    .card-niver {
        background: rgba(255, 215, 0, 0.1) !important; border: 2px solid #ffd700 !important;
        border-radius: 15px !important; padding: 10px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ROTEADOR DE PÁGINAS ---

# PÁGINA INICIAL
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div style="color:#ffd700; font-weight:900;">{p["nome"]}</div><div>{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.button("🗓️ Agenda", key="bt_1", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", key="bt_2", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", key="bt_3", on_click=navegar, args=("AnivMês",))
    with c2:
        st.button("📢 Escalas", key="bt_4", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", key="bt_5", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", key="bt_6", on_click=navegar, args=("Leitura",))
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=200)

# PÁGINA AGENDA
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED 2026</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        meses_lista = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
        cols_meses = st.columns(12)
        if 'mes_ag' not in st.session_state: st.session_state.mes_ag = hoje_br.month
        for i, (num, nome) in enumerate(meses_lista.items()):
            if cols_meses[i].button(nome, key=f"m_{num}"): st.session_state.mes_ag = num
        
        eventos = df[df['data'].dt.month == st.session_state.mes_ag].sort_values(by='data')
        for _, r in eventos.iterrows():
            st.markdown(f"**{r['data'].strftime('%d/%m')}** - {r['evento']}")

# PÁGINA GRUPOS
elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos e Departamentos</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        tabs = st.tabs(["Jovens", "Varões", "Irmãs", "Louvor", "Missões", "Tarde com Deus"])
        deptos = ["Jovens", "Varões", "Irmãs", "Louvor", "Missões", "Tarde com Deus"]
        for i, depto in enumerate(deptos):
            with tabs[i]:
                f = df[df['evento'].str.contains(depto, case=False, na=False)]
                if not f.empty:
                    for _, r in f.iterrows(): st.write(f"• {r['evento']}")
                else: st.info(f"Sem eventos para {depto}")

# PÁGINA ANIVERSARIANTES DO MÊS
elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        meses = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
        cols = st.columns(12)
        if 'mes_aniv' not in st.session_state: st.session_state.mes_aniv = hoje_br.month
        for i, (n, nome) in enumerate(meses.items()):
            if cols[i].button(nome, key=f"aniv_{n}"): st.session_state.mes_aniv = n
        lista = df[pd.to_numeric(df['mes']) == st.session_state.mes_aniv].sort_values(by='dia')
        for _, r in lista.iterrows():
            st.markdown(f"**Dia {int(r['dia']):02d}** - {r['nome']}")

# PÁGINA ESCALAS
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📅 {r.get('data','')} - {r.get('culto','')}"):
                    st.write(f"**Op:** {r.get('op','')} | **Foto:** {r.get('foto','')} | **Chegada:** {r.get('chegada','')}")
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📅 {r.get('data','')} ({r.get('dia','')})"):
                    st.write(f"**Dupla:** {r.get('dupla','')} | **Chegada:** {r.get('chegada','')}")

# PÁGINA MEDITAR (DEVOCIONAL)
elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        dt_str = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == dt_str]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"**Tema:** {d.get('tema', '')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', ''))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', ''))

# PÁGINA LEITURA (LOGIN E CADASTRO)
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Área do Leitor</h1>", unsafe_allow_html=True)
    
    if st.session_state.usuario is None:
        aba_acc = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        with aba_acc[0]:
            l_nome = st.text_input("Nome completo:").strip().title()
            l_senha = st.text_input("Senha:", type="password")
            if st.button("Acessar Plano"):
                df_u = carregar_dados("Usuarios")
                match = df_u[(df_u['nome']==l_nome) & (df_u['senha'].astype(str)==str(l_senha))]
                if not match.empty:
                    st.session_state.usuario = l_nome
                    st.rerun()
                else: st.error("Nome ou senha incorretos.")
        with aba_acc[1]:
            with st.form("form_cad"):
                n = st.text_input("Nome Completo:").strip().title()
                t = st.text_input("Telefone:")
                m = st.selectbox("Ministério:", ["Louvor", "Irmãs", "Jovens", "Varões", "Mídia", "Visitante"])
                d = st.date_input("Data Nascimento:")
                s = st.text_input("Crie uma Senha:", type="password")
                if st.form_submit_button("Finalizar Cadastro"):
                    if n and s:
                        if salvar_novo_usuario([n, t, m, str(d), s, 1, "Plano Anual"]):
                            st.success("Cadastro realizado! Faça login.")
                        else: st.error("Erro ao salvar.")
    else:
        st.write(f"Olá, **{st.session_state.usuario}**! 👋")
        if st.button("Sair da conta"): 
            st.session_state.usuario = None
            st.rerun()
        df_l = carregar_dados("Leitura")
        # Mostra leitura baseada no dia (lógica simplificada)
        st.info("Consulte seu plano de leitura diária abaixo:")
        st.dataframe(df_l, use_container_width=True)
