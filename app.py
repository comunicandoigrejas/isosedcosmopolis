import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE FUSO E DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. FUNÇÃO DE CARREGAMENTO (Google Sheets) ---
# Cole o link completo da sua planilha aqui
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=387999147#gid=387999147"

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

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILIZAÇÃO CSS (Simetria de 5 Botões) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    div.stButton > button {
        width: 100% !important; height: 65px !important; border-radius: 40px !important;
        color: white !important; font-size: 16px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 15px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }
    div.stButton:nth-of-type(5) > button { background-color: #fdcb6e !important; }
    .btn-voltar div.stButton > button { background-color: rgba(255,255,255,0.1) !important; height: 50px !important; }
    .card-niver { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; padding: 15px; border-radius: 20px; text-align: center; margin-bottom: 10px; }
    .card-escala { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border-left: 6px solid #00ffcc; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. BANCO DE DADOS AGENDA 2026 ---
agenda_2026 = {
    "Janeiro": ["16/01: Jovens", "18/01: Missões", "23/01: Varões", "30/01: Louvor", "31/01: Tarde com Deus"],
    "Fevereiro": ["06/02: Irmãs", "13/02: Jovens", "15/02: Missões", "20/02: Varões", "27/02: Louvor", "28/02: Tarde com Deus"],
    "Março": ["06/03: Irmãs", "13/03: Jovens", "15/03: Missões", "20/03: Varões", "27/03: Louvor", "28/03: Tarde com Deus"],
    "Abril": ["03/04: Irmãs", "10/04: Jovens", "17/04: Varões", "19/04: Missões", "24/04: Louvor", "25/04: Tarde com Deus"],
    "Maio": ["01/05: Irmãs", "08/05: Jovens", "15/05: Varões", "17/05: Missões", "22/05: Louvor", "30/05: Tarde com Deus"],
    "Junho": ["05/06: Jovens", "12/06: Varões", "19/06: Louvor", "21/06: Missões", "26/06: Irmãs", "27/06: Tarde com Deus"],
    "Julho": ["03/07: Jovens", "10/07: Varões", "17/07: Louvor", "19/07: Missões", "24/07: Irmãs", "25/07: Tarde com Deus"],
    "Agosto": ["07/08: Varões", "14/08: Louvor", "16/08: Missões", "21/08: Irmãs", "28/08: Jovens", "29/08: Tarde com Deus"],
    "Setembro": ["04/09: Varões", "11/09: Louvor", "18/09: Irmãs", "20/09: Missões", "25/09: Jovens", "26/09: Tarde com Deus"],
    "Outubro": ["02/10: Varões", "09/10: Louvor", "16/10: Irmãs", "18/10: Missões", "23/10: Jovens", "31/10: Tarde com Deus"],
    "Novembro": ["06/11: Louvor", "13/11: Irmãs", "15/11: Missões", "20/11: Jovens", "27/11: Varões", "28/11: Tarde com Deus"],
    "Dezembro": ["04/12: Louvor", "11/12: Irmãs", "18/12: Jovens", "20/12: Missões", "27/12: Tarde com Deus"]
}

# --- 6. LOGICA DAS PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=90)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        dia_semana = dias_pt[hoje_br.strftime('%A')]
        st.write(f"✨ {dia_semana}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    st.markdown("### 🎂 Aniversariantes da Semana")
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        # Lógica para filtrar próximos 7 dias vindo da planilha
        aniv_semana = []
        for _, r in df_niver.iterrows():
            try:
                data_aniv = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if hoje_br <= data_aniv <= (hoje_br + timedelta(days=7)):
                    aniv_semana.append(r)
            except: continue
        
        if aniv_semana:
            cols = st.columns(min(len(aniv_semana), 3))
            for i, r in enumerate(aniv_semana):
                with cols[i % 3]:
                    st.markdown(f'<div class="card-niver">🎈 <b>{r["nome"]}</b><br>{int(r["dia"]):02d}/{int(r["mes"]):02d}</div>', unsafe_allow_html=True)
        else: st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")
    else: st.warning("Aba 'Aniversariantes' não encontrada na planilha.")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.button("🎂 ANIVERSARIANTES", on_click=navegar, args=("Aniversariantes",))
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Aniversariantes":
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.title("🎂 Aniversariantes do Ano")
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        for m_num in range(1, 13):
            dados_mes = df_niver[df_niver['mes'] == m_num].sort_values(by='dia')
            if not dados_mes.empty:
                with st.expander(f"📅 {meses_nome[m_num]}", expanded=(m_num == hoje_br.month)):
                    for _, r in dados_mes.iterrows():
                        st.write(f"🎁 **Dia {int(r['dia']):02d}:** {r['nome']}")
    else: st.error("Erro ao carregar lista de aniversariantes.")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.title("📖 Meditação Diária")
    data_sel = st.date_input("Selecione o dia:", value=hoje_br, format="DD/MM/YYYY")
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
            st.success(f"📖 **Versículo:** {dev.get('versiculo', '')}")
            st.write(dev.get("texto", ""))
            if pd.notna(dev.get("aplicacao")): st.info(f"💡 **Aplicação:** {dev['aplicacao']}")
            if pd.notna(dev.get("desafio")): st.warning(f"🎯 **Desafio:** {dev['desafio']}")
        else: st.info(f"📅 Sem devocional para {data_str}.")

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda 2026")
    for mes, evs in agenda_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")
    t_mid, t_rec = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t_mid:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")}</b> - {r.get("culto","")}<br>🎧 {r.get("op","-")} | 📸 {r.get("foto","-")}</div>', unsafe_allow_html=True)
    with t_rec:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")}</b><br>👥 {r.get("dupla","-")}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Departamentos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Departamentos")
    t_tabs = st.tabs(["🌸 Irmãs", "🔥 Jovens", "🛡️ Varões", "🎤 Louvor", "🌍 Missões", "🙏 Tarde Deus"])
    termos = ["Irmãs", "Jovens", "Varões", "Louvor", "Missões", "Tarde com Deus"]
    for i, tab in enumerate(t_tabs):
        with tab:
            for mes, evs in agenda_2026.items():
                for e in evs:
                    if termos[i] in e: st.write(f"📅 **{mes}:** {e}")
