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

# Lógica: Domingo desta semana até Segunda da próxima (Janela de 9 dias)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=504320066#gid=504320066"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def registrar_leitura_log(nome, data):
    try:
        if "gcp_service_account" not in st.secrets: return False
        creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
        service = build('sheets', 'v4', credentials=creds)
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        sheet_id = match.group(1)
        values = [[nome, data]]
        body = {'values': values}
        service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range="Leitura_Log!A:B",
            valueInputOption="RAW", body=body).execute()
        return True
    except: return False

# --- 3. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state: 
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: 
    st.session_state.usuario = None

def navegar(p): 
    st.session_state.pagina = p

# --- 4. ESTILO CSS (Correção de Visibilidade e Cores) ---
st.markdown("""
    <style>
    /* Esconde elementos padrão do Streamlit */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    
    /* Fundo do App */
    [data-testid="stAppViewContainer"] { 
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); 
        color: white; 
    }
    
    .main-wrapper { max-width: 550px; margin: 0 auto; padding: 5px; }

    /* CONFIGURAÇÃO DOS BOTÕES */
    div.stButton > button {
        width: 130px !important; 
        height: 55px !important; 
        border-radius: 12px !important;
        font-size: 12px !important;
        font-weight: 900 !important; /* Fonte bem grossa */
        text-transform: uppercase !important;
        color: #FFFFFF !important; /* FORÇA TEXTO BRANCO */
        border: 1px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.4) !important;
        margin-bottom: 10px !important;
        transition: 0.3s;
    }

    /* CORES DE FUNDO ESPECÍFICAS (Forçando a cor para não ficar branco) */
    .btn-1 button { background-color: #0984e3 !important; } /* Azul */
    .btn-2 button { background-color: #e17055 !important; } /* Laranja */
    .btn-3 button { background-color: #00b894 !important; } /* Verde */
    .btn-4 button { background-color: #6c5ce7 !important; } /* Roxo */
    .btn-5 button { background-color: #fdcb6e !important; } /* Amarelo Escuro */
    .btn-6 button { background-color: #ff7675 !important; } /* Vermelho/Rosa */

    /* Efeito ao passar o mouse */
    div.stButton > button:hover {
        transform: scale(1.05);
        border: 1px solid white !important;
    }

    /* CARDS DE ANIVERSÁRIO */
    .card-niver { 
        width: 130px !important;
        height: 85px !important; 
        background: rgba(255, 215, 0, 0.15) !important; 
        border: 2px solid #ffd700 !important; 
        border-radius: 12px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }

    .niver-titulo { font-size: 1.3em !important; font-weight: 800; color: #ffd700; text-align: center; margin-bottom: 15px; text-transform: uppercase; }
    .niver-nome { font-size: 0.9em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; line-height: 1.1; padding: 2px; }
    .niver-data { font-size: 0.85em !important; font-weight: bold; color: #FFFFFF !important; margin-top: 4px; }

    /* Alinhamentos laterais */
    .btn-left div.stButton > button { margin-left: auto !important; margin-right: 5px !important; }
    .btn-right div.stButton > button { margin-right: auto !important; margin-left: 5px !important; }
    
    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px; font-weight: 800;'>ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)

    # Aniversariantes
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv = []
        for _, r in df_n.iterrows():
            try:
                data_aniv = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= data_aniv <= segunda_proxima: aniv.append(r)
            except: continue
        
        if aniv:
            st.markdown("<p class='niver-titulo'>🎊 Aniversários da semana</p>", unsafe_allow_html=True)
            cols_aniv = st.columns(len(aniv) if len(aniv) <= 4 else 4)
            for idx, p in enumerate(aniv):
                with cols_aniv[idx % 4]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="btn-left btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-left btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-left btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-right btn-2">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-right btn-4">', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-right btn-6">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=180)
    st.markdown('</div>', unsafe_allow_html=True)

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

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows(): st.info(f"📅 {r.get('data','')} - 👤 {r.get('op','N/A')}")
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows(): st.success(f"📅 {r.get('data','')} - 👥 {r.get('dupla','')}")

elif st.session_state.pagina == "Departamentos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Grupos e Departamentos")
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        tabs = st.tabs(["Irmãs", "Jovens", "Varões", "Louvor", "Missões"])
        termos = ["Irmãs", "Jovens", "Varões", "Louvor", "Missões"]
        for i, tab in enumerate(tabs):
            with tab:
                f = df[df['evento'].str.contains(termos[i], case=False, na=False)]
                for _, r in f.iterrows(): st.write(f"📅 {r['data'].strftime('%d/%m')} - {r['evento']}")

elif st.session_state.pagina == "Aniversariantes":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🎂 Todos os Aniversariantes")
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        for m in range(1, 13):
            mes = df[df['mes'] == m].sort_values(by='dia')
            if not mes.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in mes.iterrows(): st.write(f"🎁 {int(r['dia']):02d}: {r['nome']}")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditar")
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        data_busca = d_sel.strftime('%d/%m/%Y')
        hoje = df[df["data"].astype(str).str.strip() == data_busca]
        if not hoje.empty:
            d = hoje.iloc[0]
            st.header(d.get('titulo', 'Devocional'))
            st.success(f"📖 **Versículo:** {d.get('versiculo', 'N/A')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', 'Reflexão...'))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', 'Ação...'))
        else: st.warning(f"Sem devocional para {data_busca}.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📜 Plano de Leitura")
    if st.session_state.usuario is None:
        st.warning("⚠️ Identifique-se para salvar progresso.")
        n_log = st.text_input("Seu Nome Completo:")
        if st.button("Acessar"):
            df_u = carregar_dados("Usuarios_Progresso")
            u = df_u[df_u['nome'].str.lower() == n_log.lower().strip()]
            if not u.empty:
                st.session_state.usuario = u.iloc[0].to_dict()
                st.rerun()
    else:
        st.write(f"📖 Olá, **{st.session_state.usuario['nome']}**!")
        df_l = carregar_dados("Leitura")
        if not df_l.empty:
            d_hj = hoje_br.strftime('%d/%m/%Y')
            l = df_l[df_l['dia'].astype(str).str.strip() == d_hj]
            if not l.empty:
                item = l.iloc[0]
                c_at, c_nt = st.columns(2)
                with c_at: st.info(f"📜 **A.T:** {item.get('antigo_testamento','-')}")
                with c_nt: st.success(f"✝️ **N.T:** {item.get('novo_testamento','-')}")
                c_sl, c_pv = st.columns(2)
                with c_sl: st.warning(f"🎵 **Salmos:** {item.get('salmos','-')}")
                with c_pv: st.error(f"💡 **Provérbios:** {item.get('proverbios','-')}")
                if st.button("✅ CONCLUIR LEITURA"):
                    if registrar_leitura_log(st.session_state.usuario['nome'], d_hj):
                        st.balloons(); st.success("Salvo!")
