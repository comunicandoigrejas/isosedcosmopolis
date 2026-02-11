import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONFIGURAÇÃO DA PLANILHA ---
# COLOQUE APENAS A ID DA SUA PLANILHA AQUI
ID_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit"

def carregar_escalas(nome_aba):
    try:
        # Este link transforma a sua aba num arquivo CSV que o App lê instantaneamente
        url = f"https://docs.google.com/spreadsheets/d/{https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit}/gviz/tq?tqx=out:csv&sheet={nome_aba}"
        return pd.read_csv(url)
    except Exception as e:
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria Total e Design Pill) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões Pill Sincronizados (Alinhamento Vertical e Simetria Total) */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.3s !important;
        text-transform: uppercase !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 15px !important;
    }
    
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    div.stButton > button:hover { transform: scale(1.02) !important; filter: brightness(1.1) !important; }
    
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important; border: 1px solid rgba(255,255,255,0.3) !important;
        font-size: 14px !important;
    }

    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; font-size: 1.1rem; }
    .horario-chegada { color: #ffd700; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BANCO DE DADOS AGENDA 2026 (RESTAURADO) ---
agenda_2026 = {
    "Janeiro": ["16/01: 🧑‍🎓 Jovens", "18/01: 🌍 Missões", "23/01: 👔 Varões", "30/01: 🎤 Louvor", "31/01: 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02: 👗 Irmãs", "13/02: 🧑‍🎓 Jovens", "15/02: 🌍 Missões", "20/02: 👔 Varões", "27/02: 🎤 Louvor", "28/02: 🙏 Tarde com Deus"],
    "Março": ["06/03: 👗 Irmãs", "13/03: 🧑‍🎓 Jovens", "15/03: 🌍 Missões", "20/03: 👔 Varões", "27/03: 🎤 Louvor", "28/03: 🙏 Tarde com Deus"]
}

# --- 6. NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Sincronizado com Google Sheets")

    st.markdown("<br>", unsafe_allow_html=True)
    col_central = st.columns([1, 5, 1])[1]
    with col_central:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("📢 Escalas de Fevereiro")
    t_mid, t_rec = st.tabs(["📷 Mídia e Som", "🤝 Recepção"])
    
    with t_mid:
        df_midia = carregar_escalas("Midia")
        if not df_midia.empty:
            for _, row in df_midia.iterrows():
                st.markdown(f"""
                <div class="card-escala">
                    <b>{row['data']} - {row['culto']}</b><br>
                    🎧 Som: {row['op']} | 📸 Foto: {row['foto']}<br>
                    <span class="horario-chegada">⏰ Chegada: {row['chegada']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Verifique se o nome da aba é 'Midia' e se a planilha está como 'Qualquer pessoa com o link'.")

    with t_rec:
        df_recep = carregar_escalas("Recepcao")
        if not df_recep.empty:
            for _, row in df_recep.iterrows():
                st.markdown(f"""
                <div class="card-escala">
                    <b>{row['data']} ({row['dia']})</b><br>
                    👥 Dupla: {row['dupla']}<br>
                    <span class="horario-chegada">⏰ Chegada: {row['chegada']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Verifique se o nome da aba é 'Recepcao' e se a planilha está como 'Qualquer pessoa com o link'.")

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    t_irm, t_jov, t_var, t_louvor, t_mis = st.tabs(["🌸 Irmãs", "🔥 Jovens", "🛡️ Varões", "🎤 Louvor", "🌍 Missões"])
    # Lógica de filtros das abas mantida...

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Espaço Devocional")
