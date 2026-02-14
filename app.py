import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

# Lógica da Semana: Domingo (passado) até Segunda (próxima)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. ESTADO DO APP (ESSENCIAL PARA OS BOTÕES FUNCIONAREM) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p
    st.rerun() # Força o app a recarregar na página certa

# --- 3. CONEXÃO COM A PLANILHA ---
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

# --- 4. ESTILO CSS (FORÇANDO CORES E FONTES) ---
st.markdown("""
    <style>
    /* Reset Geral */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* FORÇAR COR DOS BOTÕES E TEXTOS (BRUTE FORCE) */
    div.stButton > button {
        width: 140px !important; height: 60px !important;
        border-radius: 12px !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6) !important;
    }

    /* GARANTE QUE O TEXTO DENTRO DO BOTÃO SEJA VISÍVEL */
    div.stButton > button p, div.stButton > button span {
        color: white !important;
        font-weight: 900 !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
    }

    /* CORES ESPECÍFICAS PARA CADA BOTÃO */
    .btn-agenda button { background-color: #0984e3 !important; }
    .btn-escalas button { background-color: #e17055 !important; }
    .btn-grupos button { background-color: #00b894 !important; }
    .btn-meditar button { background-color: #6c5ce7 !important; }
    .btn-leitura button { background-color: #ff7675 !important; }
    
    /* ANIVERSÁRIOS: AMARELO COM LETRA PRETA PARA LER MELHOR */
    .btn-aniv button { background-color: #f1c40f !important; }
    .btn-aniv button p { color: black !important; }

    /* CARD ANIVERSÁRIOS */
    .card-niver {
        width: 145px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.15) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        text-align: center !important; margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; line-height: 1.1; }
    .niver-data { font-size: 0.9em !important; font-weight: bold; color: white; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center; color: white;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes da Semana (Domingo a Segunda)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        
        if aniv_f:
            st.markdown("<p style='text-align:center; color:#ffd700; font-weight:bold;'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            cols_aniv = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols_aniv[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu Principal + Logo
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    
    with c1:
        st.markdown('<div class="btn-agenda">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", key="ag", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-grupos">', unsafe_allow_html=True)
        st.button("👥 Grupos", key="gr", on_click=navegar, args=("Grupos",))
        st.markdown('</div><div class="btn-aniv">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", key="an", on_click=navegar, args=("Aniversariantes_Geral",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="btn-escalas">', unsafe_allow_html=True)
        st.button("📢 Escalas", key="es", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-meditar">', unsafe_allow_html=True)
        st.button("📖 Meditar", key="me", on_click=navegar, args=("Meditar",))
        st.markdown('</div><div class="btn-leitura">', unsafe_allow_html=True)
        st.button("📜 Leitura", key="le", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)

    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=180)

# --- PÁGINAS DE DESTINO (O QUE FAZ OS BOTÕES FUNCIONAREM) ---

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Devocional Diário")
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        data_str = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == data_str]
        if not hj.empty:
            d = hj.iloc[0]
            st.header(d.get('titulo', 'Meditação'))
            st.success(f"📖 **Versículo:** {d.get('versiculo', 'N/A')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', 'Para refletir...'))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', 'Ação prática...'))
        else: st.warning(f"Sem devocional para {data_str}.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📜 Plano de Leitura Anual")
    st.info("Aqui você acompanhará seu progresso bíblico diário.")
    # (Adicione aqui a lógica de login e registro que conversamos)

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda 2026")
    df = carregar_dados("Agenda")
    if not df.empty:
        st.write(df)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")
    st.write("Consulte aqui as escalas de Mídia e Recepção.")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Grupos e Departamentos")
    st.write("Informações sobre Jovens, Irmãs, Varões e Louvor.")

elif st.session_state.pagina == "Aniversariantes_Geral":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🎂 Aniversariantes do Mês")
    st.write("Veja a lista completa de todos os aniversariantes.")
