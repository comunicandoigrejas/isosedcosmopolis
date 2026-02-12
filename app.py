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

# Dicionários de tradução para Português
meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
# IMPORTANTE: Substitua pelo link real da sua planilha configurada como "Qualquer pessoa com o link"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?gid=1520812789#gid=1520812789"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normalização de nomes de colunas (remove acentos e espaços)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a') for c in df.columns]
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 3. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 4. ESTILO CSS (Design Responsivo e Moderno) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    
    .button-container { max-width: 450px; margin: 0 auto; padding: 10px; }
    
    div.stButton > button {
        width: 100% !important; height: 60px !important; border-radius: 40px !important;
        color: white !important; font-size: 16px !important; font-weight: bold !important;
        text-transform: uppercase !important; margin-bottom: 12px !important;
        border: 2px solid rgba(255,255,255,0.1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    
    /* Cores dos 5 Botões do Menu */
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }
    div.stButton:nth-of-type(5) > button { background-color: #fdcb6e !important; }
    
    .btn-voltar div.stButton > button { background-color: rgba(255,255,255,0.1) !important; height: 45px !important; font-size: 12px !important; }

    /* Estilo dos Cards de Aniversário (Pares Compactos) */
    .card-niver { 
        background: rgba(255, 215, 0, 0.1); 
        border: 1px solid #ffd700; 
        padding: 5px; 
        border-radius: 12px; 
        text-align: center; 
        margin-bottom: 10px;
        font-size: 0.85em;
        width: 100%;
    }
    
    .card-escala { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 20px; border-left: 6px solid #00ffcc; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DAS PÁGINAS ---

# --- PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=80)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write(f"✨ {dias_pt[hoje_br.strftime('%A')]}, {hoje_br.day} de {meses_nome[hoje_br.month]}")

    st.markdown("<h3 style='text-align: center;'>🎂 Aniversariantes da Semana</h3>", unsafe_allow_html=True)
    
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        aniv_semana = []
        for _, r in df_niver.iterrows():
            try:
                d_n = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if hoje_br <= d_n <= (hoje_br + timedelta(days=7)): aniv_semana.append(r)
            except: continue
        
        if aniv_semana:
            _, centro, _ = st.columns([0.5, 3, 0.5])
            with centro:
                for i in range(0, len(aniv_semana), 2):
                    par = aniv_semana[i:i+2]
                    cols = st.columns(2)
                    for idx, pessoa in enumerate(par):
                        with cols[idx]:
                            st.markdown(f'<div class="card-niver">🎈 <b>{pessoa["nome"]}</b><br>{int(pessoa["dia"]):02d}/{int(pessoa["mes"]):02d}</div>', unsafe_allow_html=True)
        else:
            st.info("Nenhum aniversariante nos próximos 7 dias. 🙏")

    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
    st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
    st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
    st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))
    st.button("🎂 ANIVERSARIANTES", on_click=navegar, args=("Aniversariantes",))
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Agenda 2026")
    df_ag = carregar_dados("Agenda")
    if not df_ag.empty:
        df_ag['data'] = pd.to_datetime(df_ag['data'], dayfirst=True)
        for m in range(1, 13):
            mes_ev = df_ag[df_ag['data'].dt.month == m].sort_values(by='data')
            if not mes_ev.empty:
                with st.expander(f"📅 {meses_nome[m]}", expanded=(m == hoje_br.month)):
                    for _, r in mes_ev.iterrows():
                        st.write(f"• **{r['data'].strftime('%d/%m')}:** {r['evento']}")
    else: st.error("Erro ao carregar Agenda.")

# --- PÁGINA DEPARTAMENTOS ---
elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Departamentos")
    df_ag = carregar_dados("Agenda")
    if not df_ag.empty:
        df_ag['data'] = pd.to_datetime(df_ag['data'], dayfirst=True)
        tabs = st.tabs(["🌸 Irmãs", "🔥 Jovens", "🛡️ Varões", "🎤 Louvor", "🌍 Missões", "🙏 Tarde Deus"])
        termos = ["Irmãs", "Jovens", "Varões", "Louvor", "Missões", "Tarde com Deus"]
        for i, tab in enumerate(tabs):
            with tab:
                filtro = df_ag[df_ag['evento'].str.contains(termos[i], case=False, na=False)].sort_values(by='data')
                if not filtro.empty:
                    for _, r in filtro.iterrows():
                        st.write(f"📅 **{r['data'].strftime('%d/%m/%Y')}** - {r['evento']}")
                else: st.info(f"Sem eventos agendados para {termos[i]}.")

# --- PÁGINA ANIVERSARIANTES ---
elif st.session_state.pagina == "Aniversariantes":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🎂 Aniversariantes do Ano")
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        for m in range(1, 13):
            d_m = df_n[df_n['mes'] == m].sort_values(by='dia')
            if not d_m.empty:
                with st.expander(f"📅 {meses_nome[m]}", expanded=(m == hoje_br.month)):
                    for _, r in d_m.iterrows(): st.write(f"🎁 **Dia {int(r['dia']):02d}:** {r['nome']}")

# --- PÁGINA DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Meditação Diária")
    d_sel = st.date_input("Data:", value=hoje_br, format="DD/MM/YYYY")
    df_d = carregar_dados("Devocional")
    if not df_d.empty:
        hoje = df_d[df_d["data"].astype(str).str.strip() == d_sel.strftime('%d/%m/%Y')]
        if not hoje.empty:
            dev = hoje.iloc[0]
            st.markdown("---")
            st.subheader(dev.get('titulo', 'Devocional'))
            st.success(f"📖 **{dev.get('versiculo', '')}**")
            st.write(dev.get("texto", ""))
        else: st.info("Sem meditação para esta data.")

# --- PÁGINA ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Escalas")
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")}</b><br>{r.get("culto","")}</div>', unsafe_allow_html=True)
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                st.markdown(f'<div class="card-escala"><b>{r.get("data","")}</b><br>👥 {r.get("dupla","")}</div>', unsafe_allow_html=True)
