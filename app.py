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

# Lógica: Domingo que passou até Segunda que vem (Janela de 9 dias)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA (Link Salvo) ---
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

# --- 4. ESTILO CSS (FORÇANDO CONTRASTE TOTAL) ---
st.markdown("""
    <style>
    /* 1. Reset de Fundo e Esconder Lixo */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* 2. FORÇAR CABEÇALHOS EM BRANCO PURO */
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
    }

    /* 3. ESTILO DOS BOTÕES (Blindagem contra o Branco) */
    /* Target direto no botão secundário do Streamlit */
    button[data-testid="stBaseButton-secondary"] {
        width: 150px !important;
        height: 65px !important;
        border-radius: 15px !important;
        border: 2px solid rgba(255,255,255,0.4) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.5) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* FORÇAR COR DO TEXTO (O segredo para não sumir) */
    button[data-testid="stBaseButton-secondary"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }

    /* 4. CORES INDIVIDUAIS (Usando Classes de Wrapper) */
    .btn-blue button { background-color: #0984e3 !important; }
    .btn-green button { background-color: #00b894 !important; }
    .btn-orange button { background-color: #e17055 !important; }
    .btn-purple button { background-color: #6c5ce7 !important; }
    .btn-red button { background-color: #ff7675 !important; }
    
    /* Amarelo com Letra PRETA para contraste */
    .btn-yellow button { background-color: #f1c40f !important; }
    .btn-yellow button p { color: #000000 !important; }

    /* 5. CARDS DE ANIVERSÁRIO */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.9em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes (Mariane e Fátima juntas se for a semana delas)
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
    
    # MENU PRINCIPAL (2 Colunas + Logo à direita)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2.5])
    
    with c1:
        st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="ag", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-green">', unsafe_allow_html=True)
        st.button("👥 Grupos", key="gr", on_click=navegar, args=("Grupos",))
        st.markdown('</div><div class="btn-yellow">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="an", on_click=navegar, args=("AnivGeral",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="btn-orange">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="es", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-purple">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="me", on_click=navegar, args=("Meditar",))
        st.markdown('</div><div class="btn-red">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="le", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)

# --- BLOCO DE PÁGINAS (Faz os botões funcionarem) ---

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    st.write("Consulte as escalas de Mídia e Recepção aqui.")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos</h1>", unsafe_allow_html=True)
    st.write("Informações sobre Jovens, Irmãs e Varões.")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    # Lógica do Devocional...

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)
    st.info("Acesse seu progresso bíblico.")

elif st.session_state.pagina == "AnivGeral":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
