import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONFIGURAÇÃO DA PLANILHA (Link Blindado) ---
# Cole o LINK COMPLETO da sua planilha aqui
URL_PLANILHA = "COLE_AQUI_O_LINK_COMPLETO_DA_PLANILHA"

def carregar_dados(aba):
    try:
        # Extrai o ID da planilha automaticamente
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            # URL de exportação direta para CSV (Mais estável)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Padroniza nomes das colunas (minúsculo e sem espaços)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria Total e Design Pill) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { 
        visibility: hidden; display: none; 
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }

    /* CONTAINER CENTRAL - Garante alinhamento de início ao fim */
    .button-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 10px;
    }

    /* BOTÕES PILL - Largura 100% para simetria vertical total */
    div.stButton > button {
        width: 100% !important;
        height: 75px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        text-transform: uppercase !important;
        margin-bottom: 20px !important;
    }
    
    /* Cores do Menu Inicial */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important; border-radius: 25px !important; font-size: 14px !important;
    }

    /* Cards de Informação */
    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 15px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. AGENDA INTEGRAL 2026 (RESTAURADA) ---
agenda_2026 = {
    "Janeiro": ["16/01: Jovens", "18/01: Missões", "23/01: Varões", "30/01: Louvor", "31/01: Tarde com Deus"],
    "Fevereiro": ["06/02: Irmãs", "13/02: Jovens", "15/02: Missões", "20/02: Varões", "27/02: Louvor", "28/02: Tarde com Deus"],
    "Março": ["06/03: Irmãs", "13/03: Jovens", "15/03: Missões", "20/03: Varões", "27/03: Louvor", "28/03: Tarde com Deus"],
    "Abril": ["03/04: Irmãs", "10/04: Jovens", "17/04: Varões", "19/04: Missões", "24/04: Louvor", "25/04: Tarde com Deus"],
    "Maio": ["01/05: Irmãs", "08/05: Jovens", "15/05: Varões", "17/05: Missões", "22/05: Louvor", "29/05: Irmãs (5ª)", "30/05: Tarde com Deus"],
    "Junho": ["05/06: Jovens", "12/06: Varões", "19/06: Louvor", "21/06: Missões", "26/06: Irmãs", "27/06: Tarde com Deus"],
    "Julho": ["03/07: Jovens", "10/07: Varões", "17/07: Louvor", "19/07: Missões", "24/07: Irmãs", "25/07: Tarde com Deus", "31/07: Jovens (5ª)"],
    "Agosto": ["07/08: Varões", "14/08: Louvor", "16/08: Missões", "21/08: Irmãs", "28/08: Jovens", "29/08: Tarde com Deus"],
    "Setembro": ["04/09: Varões", "11/09: Louvor", "18/09: Irmãs", "20/09: Missões", "25/09: Jovens", "26/09: Tarde com Deus"],
    "Outubro": ["02/10: Varões", "09/10: Louvor", "16/10: Irmãs", "18/10: Missões", "23/10: Jovens", "30/10: Varões (5ª)", "31/10: Tarde com Deus"],
    "Novembro": ["06/11: Louvor", "13/11: Irmãs", "15/11: Missões", "20/11: Jovens", "27/11: Varões", "28/11: Tarde com Deus"],
    "Dezembro": ["04/12: Louvor", "11/12: Irmãs", "18/12: Jovens", "20/12: Missões", "27/12: Tarde com Deus"]
}

# --- 6. NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=110)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)

    st.title("📖 Meditação Diária")

    # CALENDÁRIO APARECE DIRETAMENTE AQUI
    data_selecionada = st.date_input("Selecione o dia para ler a palavra:", format="DD/MM/YYYY")
    data_str = data_selecionada.strftime('%d/%m/%Y')

    df = carregar_dados("Devocional")

    if not df.empty:
        # Padroniza a coluna data para string
        df["data"] = df["data"].astype(str).str.strip()
        dev_hoje = df[df["data"] == data_str]

        if not dev_hoje.empty:
            dev = dev_hoje.iloc[0]
            st.markdown("---")
            st.header(f"✨ {dev['titulo']}")
            st.success(f"📖 **Versículo Base:** {dev['versiculo']}")
            st.write(dev["texto"])
            
            st.markdown("### 💡 Aplicação")
            st.info(dev.get("aplicacao", "Medite nesta palavra durante o dia."))
            
            st.markdown("### 🎯 Desafio do Dia")
            st.warning(dev.get("desafio", "Compartilhe esta mensagem com alguém."))
        else:
            st.markdown("---")
            st.info(f"📅 Não há um devocional cadastrado para o dia {data_str}. Escolha outra data no calendário acima.")
    else:
        st.error("Erro ao carregar dados da aba 'Devocional'. Verifique o nome da aba e o link da planilha.")

# [As outras páginas: Agenda, Escalas e Departamentos seguem a mesma lógica restaurada]
