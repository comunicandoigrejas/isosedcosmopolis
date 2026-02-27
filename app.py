import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import calendar

# =========================================================
# 1. CONFIGURAÇÕES E ESTILO MOBILE-FIRST
# =========================================================
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; font-weight: 800; margin-bottom: 10px; }
    
    /* Layout para Celular - Botões Grandes */
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 12px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3.8em; margin-bottom: 10px;
    }
    
    /* Cards de Escala e Informativos */
    .card-isosed {
        background: rgba(255, 215, 0, 0.08) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 15px; padding: 15px; margin-bottom: 15px;
    }
    
    /* Tabelas e Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(255,255,255,0.05); border-radius: 5px; padding: 5px 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 2. CONEXÃO MESTRA (GOOGLE SHEETS)
# =========================================================
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # --- INSIRA SEU ID AQUI ---
        ID_PLANILHA = "1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0"
        return client.open_by_key(ID_PLANILHA)
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            return pd.DataFrame(aba.get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

def atualizar_contador():
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Acessos")
        valor = int(aba.acell('A2').value or 0) + 1
        aba.update_acell('A2', valor)
        return valor
    except: return "---"

# =========================================================
# 3. ROTEADOR DE PÁGINAS
# =========================================================

# --- PÁGINA INICIAL ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Informação da Santa Ceia (Lógica: Geralmente 1º Domingo do Mês)
    prox_mes = (hoje_br.month % 12) + 1
    st.markdown(f"""
        <div class="card-isosed" style="text-align: center; border-left: 5px solid #ffd700;">
            <h4 style="margin:0; color:#ffd700;">🍇 Santa Ceia do Senhor</h4>
            <p style="margin:5px 0;">Todo 1º Domingo do Mês às 18h00</p>
        </div>
    """, unsafe_allow_html=True)

    # Resumo de Aniversariantes do Mês
    df_niver = carregar_dados("Aniversariantes")
    mes_atual_nome = calendar.month_name[hoje_br.month].capitalize()
    
    st.markdown(f"<p style='text-align:center;'>🎂 <b>Aniversariantes de {mes_atual_nome}</b></p>", unsafe_allow_html=True)
    # Lógica simples para mostrar os próximos 3 aniversariantes na home
    if not df_niver.empty:
        # Assume colunas: Nome, Dia, Mes
        hoje_dia = hoje_br.day
        niver_mes = df_niver[df_niver['Mes'] == hoje_br.month].sort_values('Dia')
        proximos = niver_mes[niver_mes['Dia'] >= hoje_dia].head(3)
        if not proximos.empty:
            texto_niver = ", ".join([f"{r['Nome']} ({r['Dia']})" for _, r in proximos.iterrows()])
            st.markdown(f"<p style='text-align:center; font-size:0.9em; opacity:0.8;'>{texto_niver}</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Menu de Botões (Layout Celular)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="btn_ag")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="btn_an")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="btn_gs")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="btn_es")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), key="btn_me")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="btn_le")

    # Rodapé com Logo e Contador
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    if 'visitas' not in st.session_state: st.session_state.visitas = atualizar_contador()
    st.markdown(f"<p style='text-align:center; opacity:0.4; font-size:0.7em;'>Visitante nº: {st.session_state.visitas}</p>", unsafe_allow_html=True)

# --- PÁGINA AGENDA (Separada por Meses) ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda 2026</h2>", unsafe_allow_html=True)
    
    df_ag = carregar_dados("Agenda")
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    tabs_mes = st.tabs(meses_nomes)
    
    if not df_ag.empty:
        df_ag['data_dt'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        for i, tab in enumerate(tabs_mes):
            with tab:
                mes_data = df_ag[df_ag['data_dt'].dt.month == (i+1)].sort_values('data_dt')
                if not mes_data.empty:
                    for _, r in mes_data.iterrows():
                        st.markdown(f"**{r['data_dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos.")

# --- PÁGINA ANIVERSÁRIOS (Separada por Meses) ---
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Aniversariantes</h2>", unsafe_allow_html=True)
    
    df_an = carregar_dados("Aniversariantes")
    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    tabs_mes = st.tabs(meses_nomes)
    
    if not df_an.empty:
        for i, tab in enumerate(tabs_mes):
            with tab:
                mes_aniv = df_an[df_an['Mes'] == (i+1)].sort_values('Dia')
                if not mes_aniv.empty:
                    for _, r in mes_aniv.iterrows():
                        st.write(f"🎁 **Dia {r['Dia']}** - {r['Nome']}")
                else: st.info("Nenhum aniversariante.")

# --- PÁGINA MEDITAR E LEITURA ---
elif st.session_state.pagina in ["Meditar", "Leitura"]:
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown(f"<h2>📖 {st.session_state.pagina}</h2>", unsafe_allow_html=True)
    
    # Busca conteúdo da aba correspondente (Ex: aba 'Leitura')
    df_info = carregar_dados(st.session_state.pagina)
    if not df_info.empty:
        # Exibe o conteúdo mais recente (última linha)
        topico = df_info.iloc[-1]
        st.markdown(f"### {topico.get('Titulo', 'Palavra de Hoje')}")
        st.write(topico.get('Conteudo', 'Conteúdo em atualização...'))
    else:
        st.info("O conteúdo está sendo preparado pelos líderes.")

# --- PÁGINA ESCALAS (Cards Compactos) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt_obj'] = pd.to_datetime(df_e['Data'], dayfirst=True, errors='coerce')
        df_f = df_e[df_e['dt_obj'].dt.date >= hoje_br].sort_values('dt_obj')
        for _, r in df_f.iterrows():
            st.markdown(f"""
                <div class="card-isosed">
                    <b style="color:#ffd700;">{r['Data']} ({r['Dia']})</b><br>
                    <span style="font-size: 1.1em;">{r['Evento']}</span><br>
                    👤 <b>{r['Responsável']}</b><br>
                    <small>Setor: {r['Departamento']} | Horário: {r['Horário']}</small>
                </div>
            """, unsafe_allow_html=True)
