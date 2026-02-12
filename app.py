import streamlit as st
import pandas as pd
import os
import re

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONFIGURAÇÃO DA PLANILHA ---
# COLE AQUI O LINK COMPLETO DA SUA PLANILHA (O que aparece na barra de endereços)
URL_DA_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=789833748#gid=789833748"

def carregar_dados(aba):
    try:
        # Extrai o ID da planilha do link fornecido
        padrao = r"/d/([a-zA-Z0-9-_]+)"
        match = re.search(padrao, URL_DA_PLANILHA)
        if match:
            id_planilha = match.group(1)
            # Link de exportação direta (Método mais estável)
            url_final = f"https://docs.google.com/spreadsheets/d/{id_planilha}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url_final)
            # Limpa nomes de colunas (tira espaços e deixa em minúsculo)
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
        return pd.DataFrame()
    except Exception as e:
        # Se der erro, retorna vazio para não quebrar o App
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria Milimétrica e Design Pill) ---
st.markdown("""
    <style>
    /* Ocultar elementos desnecessários */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { 
        visibility: hidden; display: none; 
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }

    /* CONTAINER CENTRAL - Garante alinhamento de início ao fim */
    .main-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 20px;
    }

    /* BOTÕES PILL - Largura 100% para simetria total */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        text-transform: uppercase !important;
        margin-bottom: 20px !important;
        transition: 0.3s !important;
    }
    
    /* Cores do Menu Inicial */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    div.stButton > button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 20px rgba(255,255,255,0.2) !important;
    }

    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important; border-radius: 25px !important;
        font-size: 14px !important;
    }

    /* Cards de Escala */
    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 15px;
    }
    .card-escala b { color: #00ffcc; }
    .label-chegada { color: #ffd700; font-weight: bold; font-size: 0.85rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BANCO DE DADOS AGENDA 2026 (Integral Restaurado) ---
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

# --- 6. PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=110)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Agenda 2026")
    for mes, evs in agenda_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Escalas das Equipes")
    t_mid, t_rec = st.tabs(["📷 Mídia e Som", "🤝 Recepção"])
    
    with t_mid:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")} - {r.get("culto","")}</b><br>🎧 {r.get("op","-")} | 📸 {r.get("foto","-")}<br><span class="label-chegada">⏰ Chegada: {r.get("chegada","-")}</span></div>', unsafe_allow_html=True)
        else:
            st.error("Erro ao carregar Mídia. Verifique se a aba no Sheets chama 'Midia' e se o link está correto.")

    with t_rec:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")} ({r.get("dia","")})</b><br>👥 {r.get("dupla","-")}<br><span class="label-chegada">⏰ Chegada: {r.get("chegada","-")}</span></div>', unsafe_allow_html=True)
        else:
            st.error("Erro ao carregar Recepção. Verifique se a aba no Sheets chama 'Recepcao'.")

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    t_irm, t_jov, t_var, t_lou, t_mis, t_td = st.tabs(["🌸 Irmãs", "🔥 Jovens", "🛡️ Varões", "🎤 Louvor", "🌍 Missões", "🙏 Tarde Deus"])
    
    def exibir_filtro(termo):
        for m, evs in agenda_2026.items():
            for e in evs:
                if termo in e: st.write(f"📅 **{m}:** {e}")

    with t_irm: exibir_filtro("Irmãs")
    with t_jov: exibir_filtro("Jovens")
    with t_var: exibir_filtro("Varões")
    with t_lou: exibir_filtro("Louvor")
    with t_mis: exibir_filtro("Missões")
    with t_td: exibir_filtro("Tarde com Deus")

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)

    st.title("📖 Meditação Diária")
    st.write("Selecione uma data no calendário para ler a palavra:")

    # 1. O CALENDÁRIO (Substitui todas as caixas de seleção)
    # Ele aparece como um campo que, ao ser tocado, abre o calendário completo
    data_selecionada = st.date_input("", format="DD/MM/YYYY")
    
    # Converte para o formato de texto da planilha (Ex: 11/02/2026)
    data_str = data_selecionada.strftime('%d/%m/%Y')

    df = carregar_dados("Devocional")

    if not df.empty:
        # Garante que a coluna de data seja texto para comparação
        df["data"] = df["data"].astype(str).str.strip()
        
        # Busca o devocional do dia selecionado
        devocional_hoje = df[df["data"] == data_str]

        if not devocional_hoje.empty:
            dev = devocional_hoje.iloc[0]
            
            st.markdown("---")
            st.header(f"✨ {dev['titulo']}")
            
            # Badge de Tema
            st.markdown(f"🏷️ **Tema:** {dev['tema']}")
            
            # Card de Destaque para o Versículo
            st.success(f"📖 **Versículo Base:** {dev['versiculo']}")
            
            st.markdown("### 📝 Mensagem de Hoje")
            st.write(dev["texto"])

            # Aplicação e Desafio lado a lado
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if pd.notna(dev["aplicacao"]):
                    st.markdown("#### 💡 Aplicação")
                    st.info(dev["aplicacao"])
            with col2:
                if pd.notna(dev["desafio"]):
                    st.markdown("#### 🎯 Desafio")
                    st.warning(dev["desafio"])
        else:
            st.markdown("---")
            st.info(f"📅 Não há um devocional cadastrado para o dia {data_str}.")
            st.write("Tente navegar para outra data no calendário acima.")
    else:
        st.error("Erro ao conectar com a base de dados de devocionais.")
