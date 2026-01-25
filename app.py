import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. INICIALIZAÇÃO DO ESTADO DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

# Função para mudar de página
def mudar_pagina(nome):
    st.session_state.pagina = nome

# --- 3. ESTILIZAÇÃO CSS (Fundo, Botões Flutuantes e Cards) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    /* Esconder barra lateral para foco no menu central */
    [data-testid="stSidebar"] { display: none; }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Estilo dos Botões do Menu Principal */
    div.stButton > button {
        width: 100%;
        height: 100px;
        border-radius: 15px;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.2);
        font-size: 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00ffcc;
        color: #302b63;
        border: 2px solid #ffffff;
    }

    /* Cards de Congressos (Mantidos conforme solicitado) */
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

# --- 4. DADOS (Mantidos Rigorosamente) ---
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"},
    "Junho":     {"Irmãs": "05/06", "Jovens": "12/06", "Varões": "19/06", "Louvor": "26/06"}
}

# --- 5. NAVEGAÇÃO POR PÁGINAS ---

# --- PÁGINA INICIAL (O HUB DE BOTÕES) ---
if st.session_state.pagina == "Início":
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_logo, col_texto = st.columns([1, 3])
    with col_logo:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", width=150)
    with col_texto:
        st.title("ISOSED Cosmópolis")
        st.write("Seja bem-vindo ao nosso aplicativo oficial.")

    st.markdown("---")

    # Grade de Botões "Flutuantes"
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗓️ AGENDA 2026"): mudar_pagina("Agenda")
        if st.button("📢 REDES SOCIAIS"): mudar_pagina("Redes")
    with col2:
        if st.button("👥 DEPARTAMENTOS"): mudar_pagina("Departamentos")
        if st.button("📖 DEVOCIONAL"): mudar_pagina("Devocional")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🕒 Domingos 18h | Quartas 19h30 | Sextas 19h30")

# --- PÁGINA AGENDA (ESTRUTURA MANTIDA) ---
elif st.session_state.pagina == "Agenda":
    if st.button("⬅️ Voltar ao Início"): mudar_pagina("Início")
    st.title("🗓️ Cronograma Anual 2026")
    for mes, cultos in agenda_completa.items():
        with st.expander(f"📅 {mes}"):
            for depto, data in cultos.items():
                st.write(f"**{depto}:** {data}")

# --- PÁGINA DEPARTAMENTOS (ESTRUTURA MANTIDA) ---
elif st.session_state.pagina == "Departamentos":
    if st.button("⬅️ Voltar ao Início"): mudar_pagina("Início")
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

# --- OUTRAS PÁGINAS ---
elif st.session_state.pagina == "Redes":
    if st.button("⬅️ Voltar ao Início"): mudar_pagina("Início")
    st.title("📢 Mídia ISOSED")
    st.button("Gerador de Legendas")

elif st.session_state.pagina == "Devocional":
    if st.button("⬅️ Voltar ao Início"): mudar_pagina("Início")
    st.title("📖 Devocional")
