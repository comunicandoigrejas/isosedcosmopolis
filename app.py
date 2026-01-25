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

# --- 2. ESTILIZAÇÃO CSS (Layout e Cores) ---
st.markdown("""
    <style>
    /* Fundo em degradê verde e azul */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }

    /* Ajuste da barra lateral */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Cores de texto e títulos */
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
    }

    /* Estilo para os Cards de Destaque */
    .card-destaque {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00b09b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BARRA LATERAL (Logo e Navegação) ---
with st.sidebar:
    # Tentativa de carregar a logo
    nome_logo = "logo_igreja.png"
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
    st.write("v1.0 - Media Dept.")

# --- 4. FUNÇÕES DE APOIO ---
def destaque_semana():
    # Mapeamento resumido das sextas-feiras 2026
    agenda_destaque = {
        "2026-01-16": "Jovens", "2026-01-23": "Varões", "2026-01-30": "Louvor",
        "2026-02-06": "Irmãs", "2026-02-13": "Jovens", "2026-02-20": "Varões", "2026-02-27": "Louvor",
        "2026-03-06": "Irmãs", "2026-03-13": "Jovens", "2026-03-20": "Varões", "2026-03-27": "Louvor",
        "2026-05-01": "Irmãs (Abertura)", "2026-05-29": "Irmãs (Encerramento)"
    }
    
    hoje = datetime.now().date()
    dias_para_sexta = (4 - hoje.weekday()) % 7
    prox_sexta = hoje + timedelta(days=dias_para_sexta)
    data_iso = prox_sexta.strftime("%Y-%m-%d")
    
    if data_iso in agenda_destaque:
        depto = agenda_destaque[data_iso]
        st.markdown(f"""
        <div class="card-destaque">
            <h3 style="margin:0;">🔥 Culto desta Semana</h3>
            <p>Este próximo culto (<b>{prox_sexta.strftime('%d/%m')}</b>) será responsabilidade de: <br>
            <span style="font-size: 1.5rem; color: #00ffcc;"><b>{depto}</b></span></p>
        </div>
        """, unsafe_allow_html=True)

# --- 5. CONTEÚDO DAS PÁGINAS ---

if menu == "Início":
    st.title("Portal Igreja Só o Senhor é Deus")
    destaque_semana()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nossa Missão")
        st.write("Levar a palavra de Deus a todos os corações em Cosmópolis.")
    with col2:
        st.subheader("Horários")
        st.info("🕒 Domingos: 19h | 🕒 Terças: 20h | 🕒 Sextas: 20h")

elif menu == "Agenda 2026":
    st.title("🗓️ Agenda de Departamentos 2026")
    
    dados = [
        {"Mês": "Janeiro", "Irmãs": "-", "Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
        {"Mês": "Fevereiro", "Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
        {"Mês": "Março", "Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
        {"Mês": "Abril", "Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
        {"Mês": "Maio", "Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
    ]
    st.table(pd.DataFrame(dados))
    st.warning("Nota: Maio possui dois cultos para as Irmãs (Abertura e Encerramento).")

elif menu == "Departamentos":
    st.title("👥 Nossos Departamentos")
    t_mulheres, t_jovens, t_varoes, t_kids, t_missoes = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões"
    ])
    
    with t_mulheres:
        st.subheader("Círculo de Oração / Mulheres")
        st.write("Escalas de oração e eventos especiais das irmãs.")
        
    with t_jovens:
        st.subheader("UMAD - Mocidade")
        st.write("Agenda de congressos e ensaios do louvor jovem.")

    # (As outras abas seguem o mesmo padrão)

elif menu == "Redes Sociais":
    st.title("📢 Mídia e Comunicação")
    st.write("Espaço para os links e ferramentas do Instagram @isosedcosmopolissp.")
    st.button("Abrir Gerador de Legendas (Link)")

elif menu == "Devocional":
    st.title("📖 Devocional Diário")
    st.write("*'Lâmpada para os meus pés é tua palavra e luz, para o meu caminho.' (Salmos 119:105)*")
    st.date_input("Selecione o dia para ler o plano de leitura:")
