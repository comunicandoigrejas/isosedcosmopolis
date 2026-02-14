import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Lógica Aniversariantes: Domingo a Segunda (Janela de 9 dias)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=387999147#gid=387999147"

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
    except:
        return pd.DataFrame()

# --- 4. ESTILO CSS (Forçar Visibilidade e Cores) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* FORÇAR CABEÇALHOS EM BRANCO */
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { 
        color: #FFFFFF !important; 
        font-weight: 700 !important;
    }

    /* ESTILO DOS BOTÕES */
    div.stButton > button {
        width: 140px !important; height: 60px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
    }

    /* TEXTO DENTRO DOS BOTÕES */
    div.stButton > button p {
        color: white !important;
        font-weight: 900 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
    }

    /* CLASSES DE CORES */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-orange button { background-color: #e17055 !important; }
    .btn-green button { background-color: #00b894 !important; }
    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-red button { background-color: #ff7675 !important; }
    .btn-yellow button { background-color: #f1c40f !important; }
    .btn-yellow button p { color: black !important; }

    /* CARDS DE ANIVERSÁRIO */
    .card-niver {
        width: 140px !important; height: 85px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 0.9em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes da Semana (Ex: Pastora Fátima e Mariane)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_list = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_list.append(r)
            except: continue
        
        if aniv_list:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_list))
            for i, p in enumerate(aniv_list):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu Principal + Logo
    c1, c2, c_logo = st.columns([1.5, 1.5, 2.5])
    with c1:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="bt_ag", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        st.button("👥 Departamentos", key="bt_gr", on_click=navegar, args=("Grupos",))
        st.markdown('</div><div class="btn-yellow">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="bt_an", on_click=navegar, args=("AnivGeral",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="bt_es", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="bt_me", on_click=navegar, args=("Meditar",))
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="bt_le", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)

# PÁGINAS DE DESTINO (O Coração do Funcionamento dos Botões)
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("## 🗓️ Agenda ISOSED 2026")
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
    st.markdown("## 📢 Escalas de Serviço")
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
    st.markdown("## 👥 Departamentos")
    df = carregar_dados("Agenda")
    if not df.empty:
        tabs = st.tabs(["Irmãs", "Jovens", "Varões", "Louvor"])
        termos = ["Irmãs", "Jovens", "Varões", "Louvor"]
        for i, tab in enumerate(tabs):
            with tab:
                f = df[df['evento'].str.contains(termos[i], case=False, na=False)]
                for _, r in f.iterrows(): st.write(f"• {r['evento']}")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("## 📖 Meditar")
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        dt_str = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == dt_str]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"### {d.get('titulo', 'Devocional')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', 'N/A')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', 'Reflexão diária...'))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', 'Ação prática...'))
        else: st.warning(f"Sem devocional para {dt_str}.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("## 📜 Plano de Leitura")
    st.info("Acesse seu progresso diário de leitura bíblica.")

elif st.session_state.pagina == "AnivGeral":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("## 🎂 Aniversariantes do Mês")
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        for m in range(1, 13):
            mes = df[df['mes'] == m].sort_values(by='dia')
            if not mes.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in mes.iterrows(): st.write(f"🎁 {int(r['dia']):02d}: {r['nome']}")
