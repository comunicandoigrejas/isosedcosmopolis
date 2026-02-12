import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
import pytz

# --- 1. CONFIGURAÇÃO DE FUSO E DATA EM PORTUGUÊS ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Dicionários para tradução manual (Garante o PT-BR em qualquer servidor)
meses_pt = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
    7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
dias_semana_pt = {
    "Monday": "Segunda-feira", "Tuesday": "Terça-feira", "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira", "Friday": "Sexta-feira", "Saturday": "Sábado", "Sunday": "Domingo"
}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONFIGURAÇÃO DA PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. NAVEGAÇÃO E ESTILO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    /* Simetria dos Botões */
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    
    div.stButton > button {
        width: 100% !important; height: 75px !important; border-radius: 40px !important;
        color: white !important; font-size: 18px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 20px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    .card-info { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border-left: 6px solid #00ffcc; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BANCO DE DADOS AGENDA (FIXO) ---
agenda_2026 = {
    "Janeiro": ["16/01: Jovens", "18/01: Missões", "23/01: Varões", "30/01: Louvor", "31/01: Tarde com Deus"],
    "Fevereiro": ["06/02: Irmãs", "13/02: Jovens", "15/02: Missões", "20/02: Varões", "27/02: Louvor", "28/02: Tarde com Deus"],
    "Março": ["06/03: Irmãs", "13/03: Jovens", "15/03: Missões", "20/03: Varões", "27/03: Louvor", "28/03: Tarde com Deus"]
}

# --- 5. LÓGICA DAS PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=110)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        # Exibição da data em Português na Home
        dia_nome = dias_semana_pt[hoje_br.strftime('%A')]
        mes_nome = meses_pt[hoje_br.month]
        st.write(f"Hoje é {dia_nome}, {hoje_br.day} de {mes_nome}")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.title("📖 Meditação Diária")
    
    # Calendário em Português
    data_sel = st.date_input("Selecione o dia:", value=hoje_br, format="DD/MM/YYYY")
    
    # Texto auxiliar para confirmar a escolha do irmão em Português
    dia_sel_nome = dias_semana_pt[data_sel.strftime('%A')]
    st.write(f"📅 Lendo a palavra de: **{dia_sel_nome}, {data_sel.strftime('%d/%m/%Y')}**")

    data_str = data_sel.strftime('%d/%m/%Y')
    df = carregar_dados("Devocional")
    
    if not df.empty:
        df["data"] = df["data"].astype(str).str.strip()
        hoje = df[df["data"] == data_str]

        if not hoje.empty:
            dev = hoje.iloc[0]
            st.markdown("---")
            st.caption(f"🏷️ Tema: {dev.get('tema', 'Geral')}")
            st.header(dev.get('titulo', 'Sem Título'))
            st.success(f"📖 **Versículo Base:** {dev.get('versiculo', '')}")
            st.write(dev.get("texto", ""))
            
            if pd.notna(dev.get("aplicacao")):
                st.info(f"💡 **Aplicação:** {dev['aplicacao']}")
            if pd.notna(dev.get("desafio")):
                st.warning(f"🎯 **Desafio:** {dev['desafio']}")
        else:
            st.info(f"📅 Não há devocional cadastrado para o dia {data_str}.")
    else:
        st.error("Erro ao carregar a aba 'Devocional'.")

# (Demais páginas Agenda, Escalas e Departamentos seguem o mesmo padrão restaurado)
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda 2026")
    for mes, evs in agenda_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")
