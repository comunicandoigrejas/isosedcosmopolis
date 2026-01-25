import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ISOSED Cosmópolis - App Oficial",
    page_icon="⛪",
    layout="wide"
)

# --- 2. ESTILIZAÇÃO CSS PERSONALIZADA ---
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
    /* Estilo para os Cards de Eventos */
    .event-card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00ffcc;
        margin-bottom: 15px;
    }
    /* Estilo para as Datas de Sexta nas Abas */
    .friday-list {
        background-color: rgba(0, 0, 0, 0.2);
        padding: 12px;
        border-radius: 8px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (LOGO E NAVEGAÇÃO) ---
with st.sidebar:
    nome_logo = "logo igreja.png"
    if os.path.exists(nome_logo):
        st.image(nome_logo, width=200)
    else:
        st.title("⛪ ISOSED")
    
    st.markdown("---")
    menu = st.radio("Selecione a área:", ["Início", "Agenda 2026", "Departamentos", "Redes Sociais", "Devocional"])

# --- 4. LÓGICA DE DADOS (CALENDÁRIO SEXTA 2026) ---
# Mapeamento do rodízio: 1ª-Irmãs, 2ª-Jovens, 3ª-Varões, 4ª-Louvor, 5ª-Irmãs
calendario_sextas = {
    "Mulheres": ["02/01", "30/01", "06/02", "06/03", "03/04", "01/05", "29/05", "05/06", "03/07", "31/07", "07/08", "04/09", "02/10", "30/10", "06/11", "04/12"],
    "Jovens": ["09/01", "13/02", "13/03", "10/04", "08/05", "12/06", "10/07", "14/08", "11/09", "09/10", "13/11", "11/12"],
    "Varões": ["16/01", "20/02", "20/03", "17/04", "15/05", "19/06", "17/07", "21/08", "18/09", "16/10", "20/11", "18/12"],
    "Louvor": ["23/01", "27/02", "27/03", "24/04", "22/05", "26/06", "24/07", "28/08", "25/09", "23/10", "27/11"]
}

# --- 5. PÁGINAS ---

if menu == "Início":
    st.title("Portal ISOSED Cosmópolis")
    st.subheader("📍 Nossos Horários")
    c1, c2, c3 = st.columns(3)
    with c1: st.info("✨ **Domingos**\n\n Às 18h00")
    with c2: st.info("📖 **Quartas**\n\n Às 19h30")
    with c3: st.info("🔥 **Sextas**\n\n Às 19h30")

elif menu == "Agenda 2026":
    st.title("🗓️ Calendário de Eventos 2026")
    st.write("Acompanhe os congressos e festividades programadas.")

    # Organização por "Cards" visuais para ser mais intuitivo
    def criar_card(data, titulo, depto):
        st.markdown(f"""
        <div class="event-card">
            <small>{depto}</small><br>
            <b>{data}</b> - {titulo}
        </div>
        """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        criar_card("14 a 17 de Fevereiro", "Retiro de Carnaval", "JOVENS")
        criar_card("08 de Março (Manhã)", "Evento Especial Mulheres", "MULHERES")
        criar_card("24 e 25 de Abril", "Congresso de Varões", "VARÕES")
        criar_card("05 e 06 de Junho", "Congresso de Jovens", "JOVENS")
    with col_b:
        criar_card("14 e 15 de Agosto", "Congresso de Missões", "MISSÕES")
        criar_card("17 de Outubro (Noite)", "Outubro Rosa", "MULHERES")
        criar_card("30 e 31 de Outubro", "Congresso de Crianças", "KIDS")
        criar_card("21 de Novembro", "Conferência com a Bispa", "MULHERES")

elif menu == "Departamentos":
    st.title("👥 Cultos de Sexta-feira (Ano Todo)")
    st.write("Confira as datas de responsabilidade do seu departamento em 2026.")

    t_mulheres, t_jovens, t_varoes, t_louvor, t_kids, t_missoes = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎸 Louvor", "🎈 Kids", "🌍 Missões"
    ])

    with t_mulheres:
        st.subheader("Datas do Departamento de Mulheres")
        for data in calendario_sextas["Mulheres"]:
            st.markdown(f'<div class="friday-list">📅 Sexta-feira, {data}</div>', unsafe_allow_html=True)
        st.info("Eventos Extras: 08/03, 17/10 e 21/11")

    with t_jovens:
        st.subheader("Datas da Mocidade")
        for data in calendario_sextas["Jovens"]:
            st.markdown(f'<div class="friday-list">📅 Sexta-feira, {data}</div>', unsafe_allow_html=True)
        st.info("Eventos Extras: Retiro (Fev) e Congresso (Jun)")

    with t_varoes:
        st.subheader("Datas dos Varões")
        for data in calendario_sextas["Varões"]:
            st.markdown(f'<div class="friday-list">📅 Sexta-feira, {data}</div>', unsafe_allow_html=True)
        st.info("Evento Extra: Congresso (Abril)")

    with t_louvor:
        st.subheader("Datas do Grupo de Louvor")
        for data in calendario_sextas["Louvor"]:
            st.markdown(f'<div class="friday-list">📅 Sexta-feira, {data}</div>', unsafe_allow_html=True)

    with t_kids:
        st.subheader("Ministério Infantil")
        st.write("Cultos infantis todos os domingos às 18h.")
        st.markdown('<div class="event-card">🎈 <b>30 e 31/10:</b> Congresso de Crianças</div>', unsafe_allow_html=True)

    with t_missoes:
        st.subheader("Secretaria de Missões")
        st.write("Cultos Missionários: Todo 3º Domingo do mês.")
        st.markdown('<div class="event-card">🌍 <b>14 e 15/08:</b> Congresso de Missões</div>', unsafe_allow_html=True)

# Seções de Redes Sociais e Devocional mantêm a estrutura
elif menu == "Redes Sociais":
    st.title("📢 Mídia ISOSED")
    st.button("Abrir Gerador de Legendas")

elif menu == "Devocional":
    st.title("📖 Devocional Diário")
    st.write("Espaço para meditação.")
