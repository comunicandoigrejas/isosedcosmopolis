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

def registrar_usuario_planilha(nome, nascimento):
    try:
        if "gcp_service_account" not in st.secrets: return False
        creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build('sheets', 'v4', credentials=creds)
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        sheet_id = match.group(1)
        
        data_nasc_str = nascimento.strftime('%d/%m/%Y')
        values = [[nome.strip(), data_nasc_str, ""]] 
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Usuarios_Progresso!A:C",
            valueInputOption="RAW", body=body).execute()
        return True
    except: return False

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS UNIFORME ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    /* Container Central Unificado */
    .main-container { max-width: 500px; margin: 0 auto; padding: 10px; }
    
    /* Botões do Menu */
    div.stButton > button {
        width: 100% !important; height: 85px !important; border-radius: 20px !important;
        color: white !important; font-size: 14px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 8px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    .btn-1 button { background-color: #0984e3 !important; } .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; } .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; } .btn-6 button { background-color: #ff7675 !important; }
    
    /* Cards de Aniversariantes (Uniformizados com os botões) */
    .card-niver { 
        background: rgba(255, 215, 0, 0.1); 
        border: 1px solid #ffd700; 
        padding: 15px 5px; 
        border-radius: 20px; 
        text-align: center; 
        margin-bottom: 8px; 
        font-size: 0.85em; 
        height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .card-info { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border-left: 6px solid #00ffcc; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGICA DAS PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Header Centralizado
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=80)
    with col_r:
        st.title("ISOSED")
        st.write(f"✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    # CONTAINER CENTRAL UNIFORME
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Seção de Aniversariantes alinhada
    st.markdown("<h4 style='text-align: center; margin-bottom: 15px;'>🎂 Aniversariantes da Semana</h4>", unsafe_allow_html=True)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv = []
        for _, r in df_n.iterrows():
            try:
                d_n = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if hoje_br <= d_n <= (hoje_br + timedelta(days=7)): aniv.append(r)
            except: continue
        
        if aniv:
            for i in range(0, len(aniv), 2):
                cols = st.columns(2)
                par = aniv[i:i+2]
                for idx, p in enumerate(par):
                    with cols[idx]:
                        st.markdown(f'<div class="card-niver">🎈 <b>{p["nome"]}</b><br>{int(p["dia"]):02d}/{int(p["mes"]):02d}</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")

    st.markdown("<hr style='margin: 20px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # Menu em Grade (Alinhado com os aniversariantes)
    m1, m2 = st.columns(2)
    with m1:
        st.markdown('<div class="btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniversariantes",))
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

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows(): 
                # Agora exibindo o campo 'op' (operador/nome da pessoa)
                st.info(f"📅 {r.get('data','')} - {r.get('culto','')} | 👤 **{r.get('op','Não definido')}**")
        else: st.warning("Aba 'Midia' vazia ou não encontrada.")
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows(): 
                st.success(f"📅 {r.get('data','')} - 👥 {r.get('dupla','')}")

# (As outras páginas permanecem com a mesma lógica anterior para garantir o funcionamento total)
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda 2026")
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        for m in range(1, 13):
            evs = df[df['data'].dt.month == m].sort_values(by='data')
            if not evs.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in evs.iterrows(): st.write(f"• **{r['data'].strftime('%d/%m')}**: {r['evento']}")

elif st.session_state.pagina == "Departamentos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Grupos")
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        tabs = st.tabs(["Irmãs", "Jovens", "Varões", "Louvor", "Missões"])
        termos = ["Irmãs", "Jovens", "Varões", "Louvor", "Missões"]
        for i, tab in enumerate(tabs):
            with tab:
                f = df[df['evento'].str.contains(termos[i], case=False, na=False)]
                for _, r in f.iterrows(): st.write(f"📅 {r['data'].strftime('%d/%m')} - {r['evento']}")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Devocional")
    df = carregar_dados("Devocional")
    d_sel = st.date_input("Selecione a Data:", value=hoje_br)
    if not df.empty:
        hoje = df[df["data"].astype(str).str.strip() == d_sel.strftime('%d/%m/%Y')]
        if not hoje.empty:
            d = hoje.iloc[0]
            st.header(d.get('titulo', ''))
            st.success(f"📖 {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
        else: st.info("Sem devocional para esta data.")

elif st.session_state.pagina == "Aniversariantes":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🎂 Aniversariantes do Ano")
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        for m in range(1, 13):
            mes = df[df['mes'] == m].sort_values(by='dia')
            if not mes.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in mes.iterrows(): st.write(f"🎁 {int(r['dia']):02d}: {r['nome']}")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.usuario is None:
        t1, t2 = st.tabs(["Entrar", "Novo Cadastro"])
        with t1:
            nome_login = st.text_input("Nome Completo")
            if st.button("Acessar"):
                df_u = carregar_dados("Usuarios_Progresso")
                user = df_u[df_u['nome'].str.lower() == nome_login.lower().strip()]
                if not user.empty:
                    st.session_state.usuario = user.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Nome não encontrado.")
        with t2:
            n = st.text_input("Nome")
            d = st.date_input("Nascimento", min_value=datetime(1920,1,1))
            if st.button("Cadastrar"):
                if registrar_usuario_planilha(n, d): st.success("Sucesso! Entre pelo login.")
    else:
        st.subheader(f"📖 Plano de {st.session_state.usuario['nome']}")
        df_l = carregar_dados("Leitura")
        l = df_l[df_l['data'].astype(str).str.strip() == hoje_br.strftime('%d/%m/%Y')]
        if not l.empty:
            item = l.iloc[0]
            st.info(f"🔥 Tema: {item.get('tema','')}")
            st.header(item.get('referencia',''))
            st.write(f"*Propósito: {item.get('proposito','')}*")
            if st.button("✅ CONCLUÍDO"): st.balloons()
