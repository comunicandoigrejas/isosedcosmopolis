import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONTROLE DE NAVEGAÇÃO (Estado da Sessão) ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 3. ESTILIZAÇÃO CSS (Fundo e Botões Padronizados) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] { display: none; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Padronização dos Botões para Tamanho Único */
    div.stButton > button {
        width: 100%;
        height: 120px; /* Altura fixa para todos */
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-size: 22px;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #00ffcc;
        color: #302b63;
        border: 2px solid #ffffff;
        transform: scale(1.02);
    }

    /* Estilos das abas e cards (Mantidos conforme solicitado) */
    .card-congresso {
        background: rgba(255, 215, 0, 0.2);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ffd700;
        margin-bottom: 20px;
    }
    .data-item {
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 15px;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 3px solid #00ffcc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS MANTIDOS (RIGOROSAMENTE) ---
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"},
    "Junho":     {"Irmãs": "05/06", "Jovens": "12/06", "Varões": "19/06", "Louvor": "26/06"}
}

# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br><br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 4])
    with c_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Toque em uma das opções abaixo para navegar:")

    st.markdown("---")

    # Grade de botões com tamanho uniforme
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 REDES SOCIAIS", on_click=navegar, args=("Redes",))
    with col2:
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🕒 Domingos 18h | Quartas 19h30 | Sextas 19h30")

elif st.session_state.pagina == "Agenda":
    if st.button("⬅️ VOLTAR AO INÍCIO"): navegar("Início")
    st.title("🗓️ Cronograma Anual 2026")
    for mes, cultos in agenda_completa.items():
        with st.expander(f"📅 {mes}"):
            for depto, data in cultos.items():
                st.write(f"**{depto}:** {data}")

elif st.session_state.pagina == "Departamentos":
    if st.button("⬅️ VOLTAR AO INÍCIO"): navegar("Início")
    st.title("👥 Departamentos")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"])

    with t_mulheres:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUES:</b><br>08/03: Evento Especial (Manhã)<br>17/10: Outubro Rosa (Noite)<br>21/11: Conferência com a Bispa</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Irmãs" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Irmãs"]}</div>', unsafe_allow_html=True)

    with t_jovens:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUES:</b><br>14 a 17/02: Retiro de Jovens<br>05 e 06/06: Congresso de Jovens</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Jovens" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Jovens"]}</div>', unsafe_allow_html=True)

    with t_varoes:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>24 e 25/04: Congresso de Varões</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Varões" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Varões"]}</div>', unsafe_allow_html=True)

    with t_kids:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>30 e 31/10: Congresso de Crianças</div>', unsafe_allow_html=True)

    with t_missoes:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>14 e 15/08: Congresso de Missões<br>Todo 3º Domingo: Culto de Missões</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Redes":
    if st.button("⬅️ VOLTAR AO INÍCIO"): navegar("Início")
    st.title("📢 Mídia ISOSED")
    st.write("Gerencie o conteúdo do Instagram @isosedcosmopolissp.")

elif st.session_state.pagina == "Devocional":
    if st.button("⬅️ VOLTAR AO INÍCIO"): navegar("Início")
    st.title("📖 Espaço Devocional")
