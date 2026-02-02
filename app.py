import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 3. ESTILIZAÇÃO CSS (Clean App e Alinhamento Perfeito) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
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

    /* Botões Estilo Pill com Alinhamento Idêntico */
    div.stButton > button {
        width: 100%;
        height: 85px; /* Altura fixa para alinhamento vertical */
        border-radius: 50px;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
        transition: 0.4s;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Cores dos Botões para Identificação Visual */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7; }

    div.stButton > button:hover {
        transform: scale(1.02);
        filter: brightness(1.2);
        box-shadow: 0 0 20px rgba(255,255,255,0.2);
    }
    
    /* Botão Voltar */
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 55px;
        font-size: 14px;
        border-radius: 30px;
        border: 1px solid rgba(255,255,255,0.3);
    }

    /* Cards de Escala e Agenda */
    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 20px;
        border-left: 6px solid #00ffcc;
        margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS (Mantidos Rigorosamente) ---
agenda_completa_2026 = {
    "Janeiro": ["16/01 (Sex) – Jovens", "18/01 (Dom) – Missões", "23/01 (Sex) – Varões", "30/01 (Sex) – Louvor", "31/01 (Sáb) – Tarde com Deus"],
    "Fevereiro": ["06/02 (Sex) – Irmãs", "13/02 (Sex) – Jovens", "14 a 17/02 – Retiro", "15/02 (Dom) – Missões", "20/02 (Sex) – Varões", "27/02 (Sex) – Louvor", "28/02 (Sáb) – Tarde com Deus"],
    "Março": ["06/03 (Sex) – Irmãs", "08/03 (Dom) – Evento Mulheres", "13/03 (Sex) – Jovens", "15/03 (Dom) – Missões", "20/03 (Sex) – Varões", "27/03 (Sex) – Louvor", "28/03 (Sáb) – Tarde com Deus"]
}

escala_midia = [
    {"data": "01/02", "op": "Júnior", "foto": "Tiago (17:30)"},
    {"data": "04/02", "op": "Lucas", "foto": "Grazi (19:00)"},
    {"data": "06/02", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "08/02", "op": "Lucas", "foto": "Grazi (17:30)"},
    {"data": "11/02", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "13/02", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "15/02", "op": "Samuel", "foto": "Tiago (17:30)"},
    {"data": "18/02", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "20/02", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "22/02", "op": "Nicholas", "foto": "Grazi (17:30)"},
    {"data": "25/02", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "27/02", "op": "Samuel", "foto": "Grazi (19:00)"},
    {"data": "28/02", "op": "Nicholas", "foto": "Tiago (14:30)"}
]

escala_recepcao = [
    {"data": "04/02", "dia": "Quarta", "dupla": "Ailton e Rita"},
    {"data": "06/02", "dia": "Sexta", "dupla": "Márcia e Felipe"},
    {"data": "08/02", "dia": "Domingo", "dupla": "Simone e Elisabete"},
    {"data": "11/02", "dia": "Quarta", "dupla": "Ceia e Felipe"},
    {"data": "13/02", "dia": "Sexta", "dupla": "Ailton e Márcia"},
    {"data": "15/02", "dia": "Domingo", "dupla": "Rita e Simone"},
    {"data": "18/02", "dia": "Quarta", "dupla": "Ceia e Elisabete"},
    {"data": "20/02", "dia": "Sexta", "dupla": "Felipe e Márcia"},
    {"data": "22/02", "dia": "Domingo", "dupla": "Ailton e Simone"},
    {"data": "28/02", "dia": "Sábado", "dupla": "Ceia e Rita ✨"}
]

# --- 5. LÓGICA DE NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Restauração da Logomarca
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grade de Botões com Alinhamento Idêntico (Simétrico)
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    with col2:
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🕒 Domingos 18h | Quartas 19h30 | Sextas 19h30")

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Agenda Geral 2026")
    for mes, evs in agenda_completa_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia e Recepção")
    t_mid, t_rec = st.tabs(["📷 Mídia", "🤝 Recepção"])
    
    with t_mid:
        for it in escala_midia:
            st.markdown(f'<div class="card-escala"><b>{it["data"]}</b><br>🎧 Som: {it["op"]} | 📸 Foto: {it["foto"]}</div>', unsafe_allow_html=True)
    
    with t_rec:
        for it in escala_recepcao:
            st.markdown(f'<div class="card-escala"><b>{it["data"]} ({it["dia"]})</b><br>👥 Dupla: {it["dupla"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    t_irm, t_jov, t_var = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões"])
    # Conteúdo das abas segue a lógica original...

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Espaço Devocional")
