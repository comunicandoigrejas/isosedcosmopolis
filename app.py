import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=0#gid=0"

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

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS (Simetria entre Cards e Botões) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    /* Container Centralizado */
    .main-container { max-width: 600px; margin: 0 auto; padding: 10px; }
    
    /* ESTILO DOS BOTÕES (Igual aos Cards) */
    div.stButton > button {
        width: 100% !important; 
        height: 100px !important; /* Altura aumentada para simetria */
        border-radius: 20px !important;
        color: white !important; 
        font-size: 16px !important; 
        font-weight: bold !important;
        text-transform: uppercase !important; 
        margin-bottom: 50px !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Cores dos Botões */
    .btn-1 button { background-color: #0984e3 !important; }
    .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; }
    .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; }
    .btn-6 button { background-color: #ff7675 !important; }
    
    /* ESTILO DOS CARDS DE ANIVERSARIANTES */
    .card-niver { 
        background: rgba(255, 215, 0, 0.1); 
        border: 1px solid #ffd700; 
        border-radius: 20px; 
        text-align: center; 
        margin-bottom: 10px; 
        height: 100px; /* MESMA ALTURA DO BOTÃO */
        display: flex;
        flex-direction: column;
        justify-content: center;
        width: 100%;
    }
    
    /* Fonte aumentada para o nome */
    .niver-nome { font-size: 1.25em; font-weight: bold; color: #ffd700; margin-bottom: 2px; }
    .niver-data { font-size: 0.9em; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGICA DA PÁGINA INICIAL ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Título e Logo
    col_logo, col_texto = st.columns([1, 4])
    with col_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=80)
    with col_texto:
        st.title("ISOSED")
        st.write(f"✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # SEÇÃO ANIVERSARIANTES (Em pares para alinhar com os botões)
    st.markdown("<h4 style='text-align: center; margin-bottom: 15px;'>🎂 ANIVERSARIANTES DA SEMANA</h4>", unsafe_allow_html=True)
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
                        st.markdown(f"""
                            <div class="card-niver">
                                <div class="niver-nome">🎈 {p['nome']}</div>
                                <div class="niver-data">{int(p['dia']):02d} de {meses_nome[int(p['mes'])]}</div>
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")

    st.markdown("<hr style='opacity: 0.1; margin: 20px 0;'>", unsafe_allow_html=True)

    # MENU DE BOTÕES (2 Colunas, mesmas dimensões dos cards)
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown('<div class="btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with m_col2:
        st.markdown('<div class="btn-2">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-4">', unsafe_allow_html=True)
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-6">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# (O restante do código das páginas permanece o mesmo para carregar os dados)
