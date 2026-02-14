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

# Lógica: Domingo que passou até Segunda que vem
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA ---
# Link capturado da sua configuração
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVAcqFcPK0/edit"

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

# --- 4. ESTILO CSS (Blindagem de Cores e Fontes) ---
st.markdown("""
    <style>
    /* 1. Reset de Fundo e Remoção de Lixo Visual */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* 2. FORÇAR TÍTULOS E TEXTOS EM BRANCO PURO (Resolve o erro da imagem 585cce) */
    h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown { 
        color: #FFFFFF !important; 
    }

    /* 3. ESTILO DOS BOTÕES (Resolve o erro das imagens 57cda9 e 58d474) */
    /* Força o fundo a não ser branco e a borda a aparecer */
    div.stButton > button {
        width: 150px !important;
        height: 65px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* FORÇAR A COR DO TEXTO DENTRO DOS BOTÕES */
    div.stButton > button p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }

    /* CLASSES DE CORES PARA OS BOTÕES */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-green button { background-color: #00b894 !important; }
    .btn-orange button { background-color: #e17055 !important; }
    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-red button { background-color: #ff7675 !important; }
    
    /* Amarelo com letra PRETA para garantir leitura */
    .btn-yellow button { background-color: #f1c40f !important; }
    .btn-yellow button p { color: #000000 !important; }

    /* 4. CARDS DE ANIVERSÁRIO */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ROTEADOR DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes da Semana
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
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu e Logo
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="bt_1", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        st.button("👥 Grupos", key="bt_2", on_click=navegar, args=("Grupos",))
        st.markdown('</div><div class="btn-yellow">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="bt_3", on_click=navegar, args=("AnivMês",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="bt_4", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="bt_5", on_click=navegar, args=("Meditar",))
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="bt_6", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=200)

# BLOCOS QUE FAZEM OS BOTÕES FUNCIONAREM
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    st.write("Consulte aqui as escalas de Mídia e Recepção.")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos e Departamentos</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    # Lógica do Devocional...

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
