import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="ISOSED Cosmópolis - App Oficial",
    page_icon="⛪",
    layout="wide"
)

# --- 2. ESTILIZAÇÃO CSS (Layout e Identidade Visual) ---
st.markdown("""
    <style>
    /* Fundo em degradê Verde para Azul */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }

    /* Estilização da Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Ajuste de cores globais para leitura */
    h1, h2, h3, p, span, label, .stMarkdown {
        color: #ffffff !important;
    }

    /* Estilo para os cards de destaque */
    .card-info {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00b09b;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (Logo e Menu) ---
with st.sidebar:
    # Nome do arquivo ajustado exatamente como solicitado
    nome_logo = "logo igreja.png" 
    
    if os.path.exists(nome_logo):
        st.image(nome_logo, width=200)
    else:
        st.title("⛪ ISOSED")
        st.caption("Cosmópolis - SP")
    
    st.markdown("---")
    menu = st.radio(
        "Navegação",
        ["Início", "Agenda 2026", "Redes Sociais", "Departamentos", "Devocional"]
    )
    st.markdown("---")
    st.info("💡 Sugestão: Use o menu acima para navegar pelas áreas da igreja.")

# --- 4. CONTEÚDO DAS PÁGINAS ---

# PÁGINA INICIAL
if menu == "Início":
    st.title("Bem-vindo ao Portal ISOSED")
    st.write("Central de informações da Igreja Só o Senhor é Deus em Cosmópolis.")
    
    st.subheader("📍 Nossos Cultos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="card-info"><b>✨ Domingos</b><br>Culto de Celebração<br><b>Às 18h00</b></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="card-info"><b>📖 Quartas-feiras</b><br>Culto de Doutrina<br><b>Às 19h30</b></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="card-info"><b>🔥 Sextas-feiras</b><br>Culto de Departamentos<br><b>Às 19h30</b></div>', unsafe_allow_html=True)

# PÁGINA AGENDA GERAL
elif menu == "Agenda 2026":
    st.title("🗓️ Agenda Geral de Departamentos - 2026")
    dados_gerais = [
        {"Mês": "Janeiro", "Irmãs": "-", "Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
        {"Mês": "Fevereiro", "Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
        {"Mês": "Março", "Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
        {"Mês": "Abril", "Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
        {"Mês": "Maio", "Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
    ]
    st.table(pd.DataFrame(dados_gerais))

# PÁGINA DEPARTAMENTOS (Com datas específicas)
elif menu == "Departamentos":
    st.title("👥 Área dos Departamentos")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"
    ])
    
    with t_mulheres:
        st.subheader("Departamento de Mulheres (Irmãs)")
        st.write("📅 **Datas dos Cultos em 2026:**")
        st.success("Fevereiro: 06/02 | Março: 06/03 | Abril: 03/04 | Maio: 01/05 e 29/05")
        st.write("---")
        st.write("O Círculo de Oração acontece semanalmente. Procure a liderança para escalas.")

    with t_jovens:
        st.subheader("Departamento de Jovens (UMAD)")
        st.write("📅 **Datas dos Cultos em 2026:**")
        st.info("Janeiro: 16/01 | Fevereiro: 13/02 | Março: 13/03 | Abril: 10/04 | Maio: 08/05")
        st.write("---")
        st.write("Lembrete: Ensaios do Louvor Jovem acontecem aos sábados.")

    with t_varoes:
        st.subheader("Departamento de Varões")
        st.write("📅 **Datas dos Cultos em 2026:**")
        st.warning("Janeiro: 23/01 | Fevereiro: 20/02 | Março: 20/03 | Abril: 17/04 | Maio: 15/05")

    with t_kids:
        st.subheader("Ministério Infantil")
        st.write("As atividades com as crianças ocorrem todos os **Domingos às 18h**.")
        st.info("Coordenação: Procure a irmã responsável para escala de professores.")

    with t_missoes:
        st.subheader("Secretaria de Missões")
        st.write("Cultos missionários ocorrem conforme escala especial da igreja.")
        st.metric(label="Contribuição Missionária", value="Janeiro/2026", delta="Em dia")

# PÁGINA REDES SOCIAIS
elif menu == "Redes Sociais":
    st.title("📢 Mídia ISOSED")
    st.write("Gerencie o conteúdo do Instagram @isosedcosmopolissp.")
    st.button("Acessar Gerador de Legendas")

# PÁGINA DEVOCIONAL
elif menu == "Devocional":
    st.title("📖 Espaço Espiritual")
    st.write("Versículo do dia e planos de leitura.")
