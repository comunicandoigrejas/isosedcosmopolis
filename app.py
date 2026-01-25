import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ISOSED Cosmópolis - App Oficial",
    page_icon="⛪",
    layout="wide"
)

# --- 2. ESTILIZAÇÃO CSS (Fundo degradê e Cores) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
    }
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }
    .card-evento {
        background-color: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffffff;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (Logo e Navegação) ---
with st.sidebar:
    nome_logo = "logo igreja.png"
    if os.path.exists(nome_logo):
        st.image(nome_logo, width=200)
    else:
        st.title("⛪ ISOSED")
    
    st.markdown("---")
    menu = st.radio("Navegação", ["Início", "Agenda 2026", "Departamentos", "Redes Sociais", "Devocional"])

# --- 4. CONTEÚDO DAS PÁGINAS ---

if menu == "Início":
    st.title("Portal ISOSED Cosmópolis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("✨ **Domingos**\n\n Às 18h00\n\n*(3º Domingo: Missões)*")
    with col2:
        st.info("📖 **Quartas-feiras**\n\n Às 19h30")
    with col3:
        st.info("🔥 **Sextas-feiras**\n\n Às 19h30")

elif menu == "Agenda 2026":
    st.title("🗓️ Calendário de Grandes Eventos 2026")
    
    eventos_especiais = [
        {"Data": "14 a 17/02", "Evento": "Retiro de Jovens", "Departamento": "Jovens"},
        {"Data": "08/03 (Manhã)", "Evento": "Evento das Mulheres", "Departamento": "Mulheres"},
        {"Data": "24 e 25/04", "Evento": "Congresso de Varões", "Departamento": "Varões"},
        {"Data": "05 e 06/06", "Evento": "Congresso de Jovens", "Departamento": "Jovens"},
        {"Data": "14 e 15/08", "Evento": "Congresso de Missões", "Departamento": "Missões"},
        {"Data": "17/10 (Noite)", "Evento": "Outubro Rosa", "Departamento": "Mulheres"},
        {"Data": "30 e 31/10", "Evento": "Congresso de Crianças", "Departamento": "Kids"},
        {"Data": "21/11", "Evento": "Conferência com a Bispa", "Departamento": "Mulheres"},
    ]
    st.table(pd.DataFrame(eventos_especiais))
    st.write("📌 *Lembrete: Todo 3º domingo do mês é Culto de Missões.*")

elif menu == "Departamentos":
    st.title("👥 Departamentos")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"])

    with t_mulheres:
        st.subheader("Departamento de Mulheres")
        st.markdown('<div class="card-evento">🗓️ <b>08/03:</b> Evento Especial (Domingo de manhã)</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">🗓️ <b>17/10:</b> Outubro Rosa (Sábado à noite)</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">🗓️ <b>21/11:</b> Conferência de Mulheres com a Bispa</div>', unsafe_allow_html=True)

    with t_jovens:
        st.subheader("Mocidade (Jovens)")
        st.markdown('<div class="card-evento">🚌 <b>14 a 17/02:</b> Retiro de Jovens (Carnaval)</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">🔥 <b>05 e 06/06:</b> Congresso de Jovens</div>', unsafe_allow_html=True)

    with t_varoes:
        st.subheader("Varões")
        st.markdown('<div class="card-evento">🛡️ <b>24 e 25/04:</b> Congresso de Varões</div>', unsafe_allow_html=True)

    with t_kids:
        st.subheader("Ministério Infantil")
        st.markdown('<div class="card-evento">🎈 <b>30 e 31/10:</b> Congresso de Crianças</div>', unsafe_allow_html=True)

    with t_missoes:
        st.subheader("Secretaria de Missões")
        st.markdown('<div class="card-evento">📢 <b>Todo 3º Domingo:</b> Culto de Missões às 18h</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">🌍 <b>14 e 15/08:</b> Congresso de Missões</div>', unsafe_allow_html=True)

# As abas Redes Sociais e Devocional mantêm a estrutura anterior
