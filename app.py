import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. ESTILIZAÇÃO CSS (Degradê e Destaques) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] { background-color: rgba(255, 255, 255, 0.05); }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }
    
    .card-congresso {
        background: rgba(255, 215, 0, 0.2); /* Destaque Dourado */
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

# --- 3. BARRA LATERAL ---
with st.sidebar:
    if os.path.exists("logo igreja.png"):
        st.image("logo igreja.png", width=200)
    else:
        st.title("⛪ ISOSED")
    st.markdown("---")
    menu = st.radio("Navegação", ["Início", "Agenda 2026", "Departamentos", "Redes Sociais", "Devocional"])

# --- 4. DADOS DOS CULTOS (CORRIGIDOS) ---
# Dicionário organizado por mês para facilitar a visualização nas abas
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"},
    "Junho":     {"Irmãs": "05/06", "Jovens": "12/06", "Varões": "19/06", "Louvor": "26/06"}
    # ... seguindo a mesma lógica para o restante do ano
}

# --- 5. PÁGINAS ---

if menu == "Início":
    st.title("Portal ISOSED Cosmópolis")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("✨ **Domingos**\n\n 18h00\n(3º Dom: Missões)")
    with c2: st.info("📖 **Quartas**\n\n 19h30")
    with c3: st.info("🔥 **Sextas**\n\n 19h30")

elif menu == "Agenda 2026":
    st.title("🗓️ Cronograma Anual 2026")
    st.write("Visão geral dos meses e cultos de sexta-feira.")
    # Exibição organizada por trimestre para ser mais intuitivo
    for mes, cultos in agenda_completa.items():
        with st.expander(f"📅 {mes}"):
            for depto, data in cultos.items():
                st.write(f"**{depto}:** {data}")

elif menu == "Departamentos":
    st.title("👥 Departamentos e Eventos")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"])

    with t_mulheres:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUES:</b><br>08/03: Evento Especial (Manhã)<br>17/10: Outubro Rosa (Noite)<br>21/11: Conferência com a Bispa</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, cultos in agenda_completa.items():
            if "Irmãs" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Irmãs"]}</div>', unsafe_allow_html=True)

    with t_jovens:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUES:</b><br>14 a 17/02: Retiro de Jovens<br>05 e 06/06: Congresso de Jovens</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, cultos in agenda_completa.items():
            if "Jovens" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Jovens"]}</div>', unsafe_allow_html=True)

    with t_varoes:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>24 e 25/04: Congresso de Varões</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, cultos in agenda_completa.items():
            if "Varões" in cultos:
                st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Varões"]}</div>', unsafe_allow_html=True)

    with t_kids:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>30 e 31/10: Congresso de Crianças</div>', unsafe_allow_html=True)
        st.write("Cultos infantis todos os domingos às 18h.")

    with t_missoes:
        st.markdown('<div class="card-congresso">🌟 <b>DESTAQUE:</b><br>14 e 15/08: Congresso de Missões<br>Todo 3º Domingo: Culto de Missões</div>', unsafe_allow_html=True)

# (As seções de Redes Sociais e Devocional seguem o padrão anterior)
