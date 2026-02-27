import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import requests
import calendar

# --- 1. CONFIGURAÇÕES E MEMÓRIA ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p): st.session_state.pagina = p

# --- ESTILO MOBILE ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    .card-isosed {
        background: rgba(255, 215, 0, 0.08) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 12px; padding: 15px; margin-bottom: 15px;
    }
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 10px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3.8em;
    }
    .texto-biblico { font-style: italic; color: #ffd700; border-left: 3px solid #ffd700; padding-left: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E LIMPEZA DE DADOS ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        # COLE SEU ID AQUI:
        return gspread.authorize(creds).open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            # Limpa espaços em branco dos nomes das colunas
            df.columns = df.columns.str.strip()
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline no momento."

# =========================================================
# --- 3. PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # 🍇 Santa Ceia Dinâmica (Buscando na Agenda)
    df_ag_home = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag_home.empty:
        # Normaliza colunas para evitar erros de maiúsculas/minúsculas
        df_ag_home.columns = df_ag_home.columns.str.lower()
        col_data = 'data' if 'data' in df_ag_home.columns else df_ag_home.columns[0]
        col_ev = 'evento' if 'evento' in df_ag_home.columns else df_ag_home.columns[1]
        
        df_ag_home['dt_proc'] = pd.to_datetime(df_ag_home[col_data], dayfirst=True, errors='coerce')
        ceias = df_ag_home[df_ag_home[col_ev].str.contains("Santa Ceia", case=False, na=False)]
        ceias_futuras = ceias[ceias['dt_proc'].dt.date >= hoje_br].sort_values('dt_proc')
        if not ceias_futuras.empty:
            prox_ceia = ceias_futuras.iloc[0][col_data]

    st.markdown(f"""
        <div class="card-isosed" style="text-align:center;">
            <p style="margin:0; color:#ffd700; font-size:0.9em;">🍇 PRÓXIMA SANTA CEIA</p>
            <b style="font-size:1.3em;">{prox_ceia} às 18h00</b>
        </div>
    """, unsafe_allow_html=True)

    # 🎂 Aniversariantes do Mês (Correção Definitiva do KeyError)
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        # Mapeamento inteligente de colunas
        c_nome = next((c for c in df_niver.columns if 'nome' in c.lower()), "Nome")
        c_dia = next((c for c in df_niver.columns if 'dia' in c.lower()), "Dia")
        c_mes = next((c for c in df_niver.columns if 'mes' in c.lower() or 'mês' in c.lower()), "Mes")
        
        niver_mes = df_niver[df_niver[c_mes].astype(str) == str(hoje_br.month)]
        if not niver_mes.empty:
            # Ordena usando a coluna identificada
            niver_mes = niver_mes.sort_values(c_dia)
            nomes = ", ".join([f"{r[c_nome]} ({r[c_dia]})" for _, r in niver_mes.iterrows()])
            st.markdown(f"<p style='text-align:center; font-size:0.85em;'>🎂 <b>Aniversariantes de {calendar.month_name[hoje_br.month].capitalize()}:</b><br>{nomes}</p>", unsafe_allow_html=True)

    # Menu Mobile
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

# =========================================================
# --- 4. PÁGINAS COM SEPARAÇÃO POR MESES ---
# =========================================================

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda por Meses</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    if not df.empty:
        df.columns = df.columns.str.lower()
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                if not mes_df.empty:
                    for _, r in mes_df.iterrows():
                        st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos cadastrados.")

elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Quadro de Aniversários</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        c_nome = next((c for c in df.columns if 'nome' in c.lower()), "Nome")
        c_dia = next((c for c in df.columns if 'dia' in c.lower()), "Dia")
        c_mes = next((c for c in df.columns if 'mes' in c.lower() or 'mês' in c.lower()), "Mes")
        
        abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df[c_mes].astype(str) == str(i+1)].sort_values(c_dia)
                if not mes_df.empty:
                    for _, r in mes_df.iterrows():
                        st.write(f"🎁 **Dia {r[c_dia]}** - {r[c_nome]}")
                else: st.info("Nenhum aniversariante.")

# =========================================================
# --- 5. LEITURA E DEVOCIONAL (COLUNAS ESPECÍFICAS) ---
# =========================================================

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📜 Plano de Leitura</h2>", unsafe_allow_html=True)
    df = carregar_dados("Leitura")
    if not df.empty:
        # Colunas: Plano, Dia, Referência, Resumo para meditação
        item = df.iloc[-1]
        st.markdown(f"<div class='card-isosed'><h3>{item['Plano']}</h3><b>Dia {item['Dia']}</b></div>", unsafe_allow_html=True)
        st.info(f"📍 Referência: {item['Referência']}")
        
        texto_biblico = buscar_versiculo(item['Referência'])
        st.markdown(f'<div class="texto-biblico">{texto_biblico}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown(f"**Resumo para meditação:**\n\n{item['Resumo para meditação']}")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    df = carregar_dados("Devocional")
    if not df.empty:
        # Colunas: tema, data, titulo, versiculo, texto, aplicacao, desafio
        item = df.iloc[-1]
        st.markdown(f"<h3>{item['titulo']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; opacity:0.7;'>✨ Tema: {item['tema']} | 📅 {item['data']}</p>", unsafe_allow_html=True)
        
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(f"**Palavra:**\n\n{item['texto']}")
        
        with st.expander("🎯 Aplicação Pessoal"):
            st.write(item['aplicacao'])
        with st.expander("🔥 Desafio do Dia"):
            st.write(item['desafio'])

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        for _, r in df[df['dt'].dt.date >= hoje_br].sort_values('dt').iterrows():
            st.markdown(f'<div class="card-isosed"><b>{r["Data"]} ({r["Dia"]})</b><br>{r["Evento"]}: {r["Responsável"]}<br><small>{r["Departamento"]}</small></div>', unsafe_allow_html=True)
