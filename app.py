import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Lógica da Semana: De Domingo (passado) até Segunda (próxima)
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

meses_nome = {1:"Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho",
              7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"}
dias_pt = {"Monday":"Segunda-feira", "Tuesday":"Terça-feira", "Wednesday":"Quarta-feira",
           "Thursday":"Quinta-feira", "Friday":"Sexta-feira", "Saturday":"Sábado", "Sunday":"Domingo"}

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "COLE_AQUI_O_LINK_DA_PLANILHA"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normaliza colunas: remove acentos e deixa minúsculo
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 3. NAVEGAÇÃO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
def navegar(p): st.session_state.pagina = p

# --- 4. ESTILO CSS ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%); color: white; }
    .main-wrapper { max-width: 550px; margin: 0 auto; padding: 5px; }
    div.stButton > button, .card-niver {
        width: 130px !important; border-radius: 12px !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        box-sizing: border-box !important; margin-bottom: 10px !important; 
    }
    div.stButton > button { height: 55px !important; font-size: 11px !important; font-weight: bold !important; text-transform: uppercase !important; border: 1px solid rgba(255,255,255,0.1) !important; box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important; }
    .card-niver { height: 85px !important; background: rgba(255, 215, 0, 0.1) !important; border: 1px solid #ffd700 !important; flex-direction: column !important; padding: 5px !important; text-align: center !important; }
    .niver-titulo { font-size: 1.25em !important; font-weight: 800; color: #ffd700; margin-bottom: 15px; text-transform: uppercase; text-align: center; }
    .niver-nome { font-size: 0.9em !important; font-weight: 900; color: #ffd700; text-transform: uppercase; line-height: 1.1; }
    .niver-data { font-size: 0.85em !important; font-weight: bold; color: white; margin-top: 4px; }
    .btn-left div.stButton > button { margin-left: auto !important; margin-right: 5px !important; }
    .btn-right div.stButton > button { margin-right: auto !important; margin-left: 5px !important; }
    [data-testid="column"] { padding: 0 !important; }
    .btn-1 button { background-color: #0984e3 !important; } .btn-2 button { background-color: #e17055 !important; }
    .btn-3 button { background-color: #00b894 !important; } .btn-4 button { background-color: #6c5ce7 !important; }
    .btn-5 button { background-color: #fdcb6e !important; } .btn-6 button { background-color: #ff7675 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; margin-bottom: 20px; font-weight: 800;'>ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)

    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv = []
        for _, r in df_n.iterrows():
            try:
                data_aniv = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= data_aniv <= segunda_proxima: aniv.append(r)
            except: continue
        
        if aniv:
            st.markdown("<p class='niver-titulo'>🎊 Aniversários da semana</p>", unsafe_allow_html=True)
            # Alinhamento em linha única quando couber
            cols_aniv = st.columns(len(aniv) if len(aniv) <= 4 else 4)
            for idx, p in enumerate(aniv):
                with cols_aniv[idx % 4]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.markdown('<div class="btn-left btn-1">', unsafe_allow_html=True)
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.markdown('</div><div class="btn-left btn-3">', unsafe_allow_html=True)
        st.button("👥 Grupos", on_click=navegar, args=("Departamentos",))
        st.markdown('</div><div class="btn-left btn-5">', unsafe_allow_html=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniversariantes",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="btn-right btn-2">', unsafe_allow_html=True)
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.markdown('</div><div class="btn-right btn-4">', unsafe_allow_html=True)
        st.button("📖 Meditar", on_click=navegar, args=("Devocional",))
        st.markdown('</div><div class="btn-right btn-6">', unsafe_allow_html=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
        st.markdown('</div>', unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=180)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🗓️ Agenda 2026")
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        for m in range(1, 13):
            evs = df[df['data'].dt.month == m].sort_values(by='data')
            if not evs.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in evs.iterrows(): st.write(f"• **{r['data'].strftime('%d/%m')}**: {r['evento']}")

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📢 Escalas")
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows(): st.info(f"📅 {r.get('data','')} - 👤 {r.get('op','N/A')}")
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows(): st.success(f"📅 {r.get('data','')} - 👥 {r.get('dupla','')}")

elif st.session_state.pagina == "Departamentos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("👥 Grupos e Departamentos")
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True)
        tabs = st.tabs(["Irmãs", "Jovens", "Varões", "Louvor", "Missões"])
        termos = ["Irmãs", "Jovens", "Varões", "Louvor", "Missões"]
        for i, tab in enumerate(tabs):
            with tab:
                f = df[df['evento'].str.contains(termos[i], case=False, na=False)]
                for _, r in f.iterrows(): st.write(f"📅 {r['data'].strftime('%d/%m')} - {r['evento']}")

elif st.session_state.pagina == "Aniversariantes":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("🎂 Todos os Aniversariantes")
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        for m in range(1, 13):
            mes = df[df['mes'] == m].sort_values(by='dia')
            if not mes.empty:
                with st.expander(f"📅 {meses_nome[m]}"):
                    for _, r in mes.iterrows(): st.write(f"🎁 {int(r['dia']):02d}: {r['nome']}")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📖 Meditar")
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        data_busca = d_sel.strftime('%d/%m/%Y')
        hoje = df[df["data"].astype(str).str.strip() == data_busca]
        if not hoje.empty:
            d = hoje.iloc[0]
            st.header(d.get('titulo', 'Devocional'))
            st.success(f"📖 **Versículo:** {d.get('versiculo', 'N/A')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', 'Reflexão para hoje...'))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', 'Ação prática para hoje...'))
        else: st.warning(f"Sem devocional para {data_busca}.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.title("📜 Plano de Leitura")
    st.info("Acompanhe aqui o seu progresso de leitura bíblica.")
