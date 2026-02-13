import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_PLANILHA"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def registrar_usuario_planilha(nome, email, senha, nascimento):
    try:
        if "gcp_service_account" not in st.secrets: return False
        creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build('sheets', 'v4', credentials=creds)
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        sheet_id = match.group(1)
        
        # Formata a data para texto DD/MM/YYYY
        data_nasc_str = nascimento.strftime('%d/%m/%Y')
        values = [[nome, email, senha, data_nasc_str, ""]] 
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Usuarios_Progresso!A:E",
            valueInputOption="RAW", body=body).execute()
        return True
    except: return False

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    .menu-grid { max-width: 500px; margin: 0 auto; }
    div.stButton > button {
        width: 100% !important; height: 80px !important; border-radius: 20px !important;
        color: white !important; font-size: 14px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 5px !important;
    }
    .btn-1 button { background-color: #0984e3 !important; } .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; } .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; } .btn-6 button { background-color: #ff7675 !important; }
    .card-niver { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; padding: 5px; border-radius: 12px; text-align: center; margin-bottom: 10px; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    st.title("ISOSED Cosmópolis")
    st.write(f"✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    # Menu em Grade
    st.markdown('<div class="menu-grid">', unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown('<div class="btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniv.", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="btn-2">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-4">', unsafe_allow_html=True)
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-6">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. PÁGINA LEITURA (COM AUTOCADASTRO) ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    
    if st.session_state.usuario is None:
        t_login, t_cad = st.tabs(["Entrar", "Novo Cadastro"])
        with t_login:
            with st.form("login"):
                e = st.text_input("E-mail")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    df_u = carregar_dados("Usuarios_Progresso")
                    user = df_u[(df_u['email'] == e) & (df_u['senha'].astype(str) == s)]
                    if not user.empty:
                        st.session_state.usuario = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("E-mail ou senha incorretos.")
        with t_cad:
            with st.form("cadastro"):
                n = st.text_input("Como quer ser chamado?")
                e_c = st.text_input("E-mail")
                s_c = st.text_input("Crie uma senha", type="password")
                d_n = st.date_input("Data de Nascimento", min_value=datetime(1920, 1, 1), max_value=datetime.now())
                if st.form_submit_button("Criar minha conta"):
                    if registrar_usuario_planilha(n, e_c, s_c, d_n):
                        st.success("Conta criada! Já pode fazer login.")
                    else: st.error("Erro ao salvar. Verifique a aba 'Usuarios_Progresso'.")
    else:
        # Lógica de Boas-vindas e Aniversário
        nome_curto = st.session_state.usuario['nome'].split()[0]
        
        # Verifica se hoje é aniversário
        try:
            data_nasc = datetime.strptime(st.session_state.usuario['nascimento'], '%d/%m/%Y')
            if data_nasc.day == hoje_br.day and data_nasc.month == hoje_br.month:
                st.balloons()
                st.markdown(f"### 🎂 Parabéns, {nome_curto}! 🎉")
                st.info("A ISOSED celebra a sua vida hoje! Que Deus te abençoe ricamente.")
            else:
                st.markdown(f"### Olá, {nome_curto}! 👋")
        except:
            st.markdown(f"### Olá, {nome_curto}! 👋")

        st.write("Aqui está o seu plano de leitura para hoje:")
        # [Lógica da leitura diária conforme as versões anteriores]
