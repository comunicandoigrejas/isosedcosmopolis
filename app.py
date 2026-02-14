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

domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")


# --- 2. NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

if 'usuario' not in st.session_state:
    st.session_state.usuario = None


# --- 3. CONEXÃO PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê','e').replace('ã','a').replace('ç','c') for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()


def conectar_planilha():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    return client.open_by_url(URL_PLANILHA)


def salvar_novo_usuario(lista_dados):
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Usuarios")
        aba.append_row(lista_dados)
        return True
    except Exception as e:
        st.error(f"Erro ao gravar na planilha: {e}")
        return False


# ======================= PÁGINAS =======================

# -------- INÍCIO --------
if st.session_state.pagina == "Início":

    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    df_n = carregar_dados("Aniversariantes")

    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima:
                    aniv_f.append(r)
            except:
                continue

        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(
                        f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div>'
                        f'<div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>',
                        unsafe_allow_html=True
                    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c_logo = st.columns([1.5,1.5,2])
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", on_click=navegar, args=("P_Leitura",))
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=200)


# -------- AGENDA --------
elif st.session_state.pagina == "Agenda":

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED 2026</h1>", unsafe_allow_html=True)

    df = carregar_dados("Agenda")

    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['data'])

        meses = {1:"Jan",2:"Fev",3:"Mar",4:"Abr",5:"Mai",6:"Jun",7:"Jul",8:"Ago",9:"Set",10:"Out",11:"Nov",12:"Dez"}
        cols = st.columns(12)

        for i,(num,nome) in enumerate(meses.items()):
            with cols[i]:
                if st.button(nome):
                    st.session_state.mes_agenda = num
                    st.rerun()

        mes = st.session_state.get("mes_agenda", hoje_br.month)
        eventos = df[df['data'].dt.month == mes].sort_values(by="data")

        st.markdown(f"### Eventos de {meses[mes]}")

        for _,r in eventos.iterrows():
            dia = r['data'].strftime('%d/%m')
            st.markdown(f"**{dia}** — {r['evento']}")

    else:
        st.error("Erro ao carregar agenda")


# -------- GRUPOS --------
elif st.session_state.pagina == "Grupos":

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos</h1>", unsafe_allow_html=True)

    df = carregar_dados("Agenda")

    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['data'])

        deps = ["Jovens","Varões","Irmãs","Louvor","Missões","Tarde com Deus"]
        tabs = st.tabs(deps)

        for i,depto in enumerate(deps):
            with tabs[i]:
                filtro = df[df['evento'].str.contains(depto,case=False,na=False)]
                for _,r in filtro.iterrows():
                    st.write(r['data'].strftime('%d/%m/%Y'), "-", r['evento'])
    else:
        st.error("Erro ao carregar grupos")


# -------- ESCALAS --------
elif st.session_state.pagina == "Escalas":

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas</h1>", unsafe_allow_html=True)

    t1,t2 = st.tabs(["📷 Mídia","🤝 Recepção"])

    with t1:
        df = carregar_dados("Midia")
        for _,r in df.iterrows():
            st.write(r.to_dict())

    with t2:
        df = carregar_dados("Recepcao")
        for _,r in df.iterrows():
            st.write(r.to_dict())


# -------- MEDITAR --------
elif st.session_state.pagina == "Meditar":

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)

    d_sel = st.date_input("Escolha:", value=hoje_br)
    df = carregar_dados("Devocional")

    if not df.empty:
        dt = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip()==dt]
        if not hj.empty:
            st.write(hj.iloc[0].to_dict())
        else:
            st.warning("Sem devocional")


# -------- LEITURA --------
elif st.session_state.pagina == "P_Leitura":

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)

    if st.session_state.usuario is None:
        nome = st.text_input("Nome:")
        if st.button("Entrar"):
            if nome:
                st.session_state.usuario = nome
                st.rerun()
    else:
        st.write("Usuário:", st.session_state.usuario)
