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
# Se hoje for Sábado (14/02), o domingo foi 08/02 e a segunda será 16/02
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=504320066"

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

# --- 3. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): 
    st.session_state.pagina = p

# --- 4. ESTILO CSS (O "Tanque de Guerra" contra o Branco no Branco) ---
st.markdown("""
    <style>
    /* Reset Geral */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; color: white !important; }

    /* SELETOR PARA O TEXTO DENTRO DOS BOTÕES (A parte mais difícil) */
    /* Isso garante que a letra NÃO fique branca se o fundo for claro */
    [data-testid="stBaseButton-secondary"] p {
        color: white !important;
        font-weight: 900 !important;
        font-size: 11px !important;
    }

    /* ESTILO DOS BOTÕES */
    [data-testid="stBaseButton-secondary"] {
        width: 140px !important;
        height: 60px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
        transition: 0.3s !important;
    }

    /* CORES DE FUNDO POR CLASSE */
    .blue-btn [data-testid="stBaseButton-secondary"] { background-color: #0984e3 !important; }
    .orange-btn [data-testid="stBaseButton-secondary"] { background-color: #e17055 !important; }
    .green-btn [data-testid="stBaseButton-secondary"] { background-color: #00b894 !important; }
    .purple-btn [data-testid="stBaseButton-secondary"] { background-color: #6c5ce7 !important; }
    .red-btn [data-testid="stBaseButton-secondary"] { background-color: #ff7675 !important; }
    
    /* Amarelo com letra PRETA para conseguir ler */
    .yellow-btn [data-testid="stBaseButton-secondary"] { background-color: #f1c40f !important; }
    .yellow-btn [data-testid="stBaseButton-secondary"] p { color: black !important; }

    /* CARD DE ANIVERSÁRIO - CENTRALIZADO */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important; text-align: center !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; line-height: 1.1; }
    .niver-data { font-size: 0.9em !important; font-weight: bold; color: white; margin-top: 5px; }
    
    [data-testid="column"] { padding: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DA PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center; color: white;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # 1. ANIVERSARIANTES (Domingo a Segunda na mesma linha)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_list = []
        for _, r in df_n.iterrows():
            try:
                d_a = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= d_a <= segunda_proxima: aniv_list.append(r)
            except: continue
        
        if aniv_list:
            st.markdown("<p style='text-align:center; color:#ffd700; font-weight:bold;'>🎊 ANIVERSÁRIOS DA SEMANA</p>", unsafe_allow_html=True)
            # Todos na mesma linha (ex: Pastora Fátima e Mariane)
            cols_aniv = st.columns(len(aniv_list))
            for idx, p in enumerate(aniv_list):
                with cols_aniv[idx]:
                    st.markdown(f"""<div class="card-niver"><div class="niver-nome">{p['nome']}</div><div class="niver-data">{int(p['dia']):02d}/{int(p['mes']):02d}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. MENU + LOGO (Aproximados e Coloridos)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="green-btn">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="yellow-btn">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="orange-btn">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="purple-btn">', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="red-btn">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=200)

# --- 6. PÁGINA DEVOCIONAL (Com Aplicação e Desafio) ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditar")
    d_sel = st.date_input("Selecione a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        data_busca = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == data_busca]
        if not hj.empty:
            d = hj.iloc[0]
            st.header(d.get('titulo', 'Devocional Diário'))
            st.success(f"📖 **Versículo:** {d.get('versiculo', 'N/A')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', 'Para refletir hoje...'))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', 'Pratique hoje...'))
        else: st.info("Sem meditação para esta data.")

# (As outras páginas elif seguem a mesma lógica das versões anteriores)
