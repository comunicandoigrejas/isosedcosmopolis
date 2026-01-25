import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ISOSED Cosmópolis - App Oficial",
    page_icon="⛪",
    layout="wide"
)

# --- 2. ESTILIZAÇÃO CSS ---
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
    .card-mensal {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL ---
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
        st.info("✨ **Domingos**\n\n Às 18h00\n\n*(3º Dom: Missões)*")
    with col2:
        st.info("📖 **Quartas-feiras**\n\n Às 19h30")
    with col3:
        st.info("🔥 **Sextas-feiras**\n\n Às 19h30")

elif menu == "Agenda 2026":
    st.title("🗓️ Calendário Geral 2026")
    st.subheader("Principais Eventos do Ano")
    
    eventos = [
        {"Mês": "Fevereiro", "Data": "14 a 17/02", "Evento": "Retiro de Jovens"},
        {"Mês": "Março", "Data": "08/03", "Evento": "Evento Mulheres (Manhã)"},
        {"Mês": "Abril", "Data": "24 e 25/04", "Evento": "Congresso de Varões"},
        {"Mês": "Junho", "Data": "05 e 06/06", "Evento": "Congresso de Jovens"},
        {"Mês": "Agosto", "Data": "14 e 15/08", "Evento": "Congresso de Missões"},
        {"Mês": "Outubro", "Data": "17/10", "Evento": "Outubro Rosa"},
        {"Mês": "Outubro", "Data": "30 e 31/10", "Evento": "Congresso Kids"},
        {"Mês": "Novembro", "Data": "21/11", "Evento": "Conf. Mulheres (Bispa)"}
    ]
    st.table(pd.DataFrame(eventos))

elif menu == "Departamentos":
    st.title("👥 Gestão por Departamento")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"])

    with t_mulheres:
        st.subheader("Departamento de Mulheres")
        st.markdown("### 📅 Cultos Mensais (Sextas-feiras)")
        st.markdown('<div class="card-mensal">Fev: 06/02 | Mar: 06/03 | Abr: 03/04 | Mai: 01/05 e 29/05</div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Eventos e Congressos")
        st.markdown('<div class="card-evento">🌸 08/03: Evento Especial (Manhã)</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">💗 17/10: Outubro Rosa (Noite)</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">👑 21/11: Conferência com a Bispa</div>', unsafe_allow_html=True)

    with t_jovens:
        st.subheader("Mocidade (Jovens)")
        st.markdown("### 📅 Cultos Mensais (Sextas-feiras)")
        st.markdown('<div class="card-mensal">Jan: 16/01 | Fev: 13/02 | Mar: 13/03 | Abr: 10/04 | Mai: 08/05</div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Eventos e Congressos")
        st.markdown('<div class="card-evento">🚌 14 a 17/02: Retiro de Jovens</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-evento">🔥 05 e 06/06: Congresso de Jovens</div>', unsafe_allow_html=True)

    with t_varoes:
        st.subheader("Varões")
        st.markdown("### 📅 Cultos Mensais (Sextas-feiras)")
        st.markdown('<div class="card-mensal">Jan: 23/01 | Fev: 20/02 | Mar: 20/03 | Abr: 17/04 | Mai: 15/05</div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Eventos e Congressos")
        st.markdown('<div class="card-evento">🛡️ 24 e 25/04: Congresso de Varões</div>', unsafe_allow_html=True)

    with t_kids:
        st.subheader("Ministério Infantil")
        st.write("Atividades todos os domingos às 18h.")
        st.markdown("### 🏆 Eventos e Congressos")
        st.markdown('<div class="card-evento">🎈 30 e 31/10: Congresso de Crianças</div>', unsafe_allow_html=True)

    with t_missoes:
        st.subheader("Secretaria de Missões")
        st.markdown('<div class="card-mensal">📢 Todo 3º Domingo do mês às 18h00</div>', unsafe_allow_html=True)
        
        st.markdown("### 🏆 Eventos e Congressos")
        st.markdown('<div class="card-evento">🌍 14 e 15/08: Congresso de Missões</div>', unsafe_allow_html=True)

elif menu == "Redes Sociais":
    st.title("📢 Mídia ISOSED")
    st.write("Acesso às ferramentas de comunicação.")
    st.button("Gerar Legendas para Instagram")

elif menu == "Devocional":
    st.title("📖 Devocional Diário")
    st.write("Espaço para leitura da Palavra e oração.")
