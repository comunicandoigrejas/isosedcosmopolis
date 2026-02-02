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

# --- 3. ESTILIZAÇÃO CSS (Clean App, Hub Pill e Simetria) ---
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

    /* Botões Pill Alinhados (Simétricos) */
    div.stButton > button {
        width: 100%;
        height: 85px;
        border-radius: 50px;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border: none;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3);
        transition: 0.4s;
        text-transform: uppercase;
    }
    
    /* Cores dos Botões (Inspirado no exemplo Pill) */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7; }

    div.stButton > button:hover {
        transform: scale(1.02);
        filter: brightness(1.2);
    }
    
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 55px; border-radius: 30px; font-size: 14px;
    }

    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BANCO DE DADOS INTEGRAL 2026 ---
# Restaurado com todas as datas fornecidas: Departamentos, Missões e Tarde com Deus
agenda_2026 = {
    "Janeiro": ["16/01: 🧑‍🎓 Jovens", "18/01: 🌍 Missões", "23/01: 👔 Varões", "30/01: 🎤 Louvor", "31/01: 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02: 👗 Irmãs", "13/02: 🧑‍🎓 Jovens", "15/02: 🌍 Missões", "20/02: 👔 Varões", "27/02: 🎤 Louvor", "28/02: 🙏 Tarde com Deus"],
    "Março": ["06/03: 👗 Irmãs", "13/03: 🧑‍🎓 Jovens", "15/03: 🌍 Missões", "20/03: 👔 Varões", "27/03: 🎤 Louvor", "28/03: 🙏 Tarde com Deus"],
    "Abril": ["03/04: 👗 Irmãs", "10/04: 🧑‍🎓 Jovens", "17/04: 👔 Varões", "19/04: 🌍 Missões", "24/04: 🎤 Louvor", "25/04: 🙏 Tarde com Deus"],
    "Maio": ["01/05: 👗 Irmãs", "08/05: 🧑‍🎓 Jovens", "15/05: 👔 Varões", "17/05: 🌍 Missões", "22/05: 🎤 Louvor", "29/05: 👗 Irmãs (5ª Sex)", "30/05: 🙏 Tarde com Deus"],
    "Junho": ["05/06: 🧑‍🎓 Jovens", "12/06: 👔 Varões", "19/06: 🎤 Louvor", "21/06: 🌍 Missões", "26/06: 👗 Irmãs", "27/06: 🙏 Tarde com Deus"],
    "Julho": ["03/07: 🧑‍🎓 Jovens", "10/07: 👔 Varões", "17/07: 🎤 Louvor", "19/07: 🌍 Missões", "24/07: 👗 Irmãs", "25/07: 🙏 Tarde com Deus", "31/07: 🧑‍🎓 Jovens (5ª Sex)"],
    "Agosto": ["07/08: 👔 Varões", "14/08: 🎤 Louvor", "16/08: 🌍 Missões", "21/08: 👗 Irmãs", "28/08: 🧑‍🎓 Jovens", "29/08: 🙏 Tarde com Deus"],
    "Setembro": ["04/09: 👔 Varões", "11/09: 🎤 Louvor", "18/09: 👗 Irmãs", "20/09: 🌍 Missões", "25/09: 🧑‍🎓 Jovens", "26/09: 🙏 Tarde com Deus"],
    "Outubro": ["02/10: 👔 Varões", "09/10: 🎤 Louvor", "16/10: 👗 Irmãs", "18/10: 🌍 Missões", "23/10: 🧑‍🎓 Jovens", "30/10: 👔 Varões (5ª Sex)", "31/10: 🙏 Tarde com Deus"],
    "Novembro": ["06/11: 🎤 Louvor", "13/11: 👗 Irmãs", "15/11: 🌍 Missões", "20/11: 🧑‍🎓 Jovens", "27/11: 👔 Varões", "28/11: 🙏 Tarde com Deus"],
    "Dezembro": ["04/12: 🎤 Louvor", "11/12: 👗 Irmãs", "18/12: 🧑‍🎓 Jovens", "20/12: 🌍 Missões", "25/12: ❌ Sem culto", "27/12: 🙏 Tarde com Deus"]
}

# --- 5. LÓGICA DE NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    with col2:
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    
    st.info("🕒 Domingos 18h | Quartas 19h30 | Sextas 19h30")

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Agenda Geral 2026")
    for mes, evs in agenda_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia e Recepção")
    t_midia, t_recep = st.tabs(["📷 Mídia", "🤝 Recepção"])
    
    with t_midia:
        st.subheader("Fevereiro/2026")
        # Dados das fotos restaurados
        midia_fev = [
            {"d": "01/02", "op": "Júnior", "ft": "Tiago (17:30)"},
            {"d": "04/02", "op": "Lucas", "ft": "Grazi (19:00)"},
            {"d": "06/02", "op": "Samuel", "ft": "Tiago (19:00)"},
            {"d": "08/02", "op": "Lucas", "ft": "Grazi (17:30)"}
        ]
        for it in midia_fev:
            st.markdown(f'<div class="card-escala"><b>{it["d"]}</b><br>🎧 Som: {it["op"]} | 📸 Foto: {it["ft"]}</div>', unsafe_allow_html=True)

    with t_recep:
        st.subheader("Fevereiro/2026")
        recep_fev = [{"d": "04/02", "dp": "Ailton e Rita"}, {"d": "06/02", "dp": "Márcia e Felipe"}]
        for it in recep_fev:
            st.markdown(f'<div class="card-escala"><b>{it["d"]}</b><br>👥 Dupla: {it["dp"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    t_mul, t_jov, t_var, t_mis = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🌍 Missões"])
    
    with t_jov:
        for mes, evs in agenda_2026.items():
            for ev in evs:
                if "Jovens" in ev: st.write(f"📅 **{mes}:** {ev}")

    with t_mis:
        for mes, evs in agenda_2026.items():
            for ev in evs:
                if "Missões" in ev: st.write(f"📅 **{mes}:** {ev}")
