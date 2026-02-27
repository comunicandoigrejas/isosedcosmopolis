import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import calendar

# =========================================================
# 1. CONFIGURAÇÕES INICIAIS E ESTILO (CSS)
# =========================================================
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

# CSS AJUSTADO: Quadros menores e botões responsivos
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; margin-bottom: 20px; }
    
    /* QUADROS DE ESCALA (Compactos) */
    .card-isosed {
        background: rgba(255, 215, 0, 0.08) !important; 
        border: 1px solid #ffd700 !important;
        border-radius: 10px; padding: 10px; margin-bottom: 10px;
        font-size: 0.9em;
    }
    
    /* BOTÕES DO MENU */
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 8px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3em;
    }
    
    /* ESTILO AGENDA */
    .item-agenda {
        padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex; justify-content: space-between;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 2. CONEXÃO COM GOOGLE SHEETS
# =========================================================
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # --- ATENÇÃO: COLOQUE APENAS O ID (SEM O RESTO DO LINK) ---
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
# 3. ROTEADOR DE PÁGINAS (CADA ELIF É UMA PÁGINA)
# =========================================================

# --- PÁGINA 1: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; border-bottom: 3px solid #ffd700; text-align: center;">
            <p style="margin:0; font-size: 1.1em; color:#ffd700;"><b>Igreja Só o Senhor é Deus</b></p>
            <p style="opacity: 0.7; font-size:0.9em;">Cosmópolis - SP</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

    # RODAPÉ
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"):
        st.image("logo igreja.png", width=150)
    
    if 'visitas' not in st.session_state: st.session_state.visitas = atualizar_contador()
    st.markdown(f"<p style='text-align:center; opacity:0.4; font-size:0.7em;'>Visitante nº: {st.session_state.visitas}</p>", unsafe_allow_html=True)

# --- PÁGINA 2: AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda de Eventos</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        for _, r in df.iterrows():
            st.markdown(f'<div class="item-agenda"><span><b>{r["data"]}</b> - {r["evento"]}</span></div>', unsafe_allow_html=True)
    else: st.info("Nenhum evento programado.")

# --- PÁGINA 3: ANIVERSÁRIOS ---
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Aniversariantes</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else: st.info("Sem aniversariantes este mês.")

# --- PÁGINA 4: ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Próximas Escalas</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt_obj'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        df_f = df[df['dt_obj'].dt.date >= hoje_br].sort_values('dt_obj')
        for _, r in df_f.iterrows():
            st.markdown(f"""
                <div class="card-isosed">
                    <b style="color:#ffd700;">{r['Data']} - {r['Evento']}</b><br>
                    👤 {r['Responsável']} | 📍 {r['Departamento']} | ⏰ {r['Horário']}
                </div>
            """, unsafe_allow_html=True)
    else: st.info("Escalas não publicadas.")

# --- PÁGINA 5: MEDITAR ---
elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Momento de Meditação</h2>", unsafe_allow_html=True)
    st.write("Espaço para a palavra diária e reflexão.")

# --- PÁGINA 6: LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📜 Plano de Leitura Bíblica</h2>", unsafe_allow_html=True)
    st.write("Acompanhe o cronograma de leitura anual.")

# --- PÁGINA 7: GESTÃO ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("login"):
            senha = st.text_input("Senha:", type="password")
            if st.form_submit_button("Acessar"):
                if senha == "ISOSED2026": 
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta!")
    else:
        st.success("Painel do Líder")
        # (Lógica de geração de escalas aqui...)
