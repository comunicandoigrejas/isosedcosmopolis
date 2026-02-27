import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
        font-weight: bold; border: 1px solid #16213e; height: 3.5em;
    }
    .footer-text { text-align: center; opacity: 0.6; font-size: 0.8em; margin-top: 10px; }
    .social-links { text-align: center; margin: 15px 0; }
    .social-links a { color: #ffd700; text-decoration: none; margin: 0 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E FUNÇÕES AUXILIARES ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        ID_PLANILHA = "1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0"
        return gspread.authorize(creds).open_by_key(ID_PLANILHA)
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            df.columns = df.columns.str.strip() # Limpa espaços nos nomes das colunas
            return df
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

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia indisponível."

# =========================================================
# --- 3. PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # --- Card Santa Ceia ---
    df_ag_home = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag_home.empty:
        df_ag_home.columns = df_ag_home.columns.str.lower()
        df_ag_home['dt_proc'] = pd.to_datetime(df_ag_home['data'], dayfirst=True, errors='coerce')
        ceias = df_ag_home[df_ag_home['evento'].str.contains("Santa Ceia", case=False, na=False)]
        ceias_futuras = ceias[ceias['dt_proc'].dt.date >= hoje_br].sort_values('dt_proc')
        if not ceias_futuras.empty:
            prox_ceia = ceias_futuras.iloc[0]['data']

    st.markdown(f"""
        <div class="card-isosed" style="text-align:center; border-left: 5px solid #ffd700;">
            <p style="margin:0; color:#ffd700; font-size:0.8em; font-weight:bold;">🍇 PRÓXIMA SANTA CEIA</p>
            <b style="font-size:1.3em;">{prox_ceia} às 18h00</b>
        </div>
    """, unsafe_allow_html=True)

    # --- Bloco Próximos 5 Aniversariantes ---
    df_niver = carregar_dados("Aniversariantes")
    if not df_niver.empty:
        c_nome = next((c for c in df_niver.columns if 'nome' in c.lower()), "Nome")
        c_dia = next((c for c in df_niver.columns if 'dia' in c.lower()), "Dia")
        c_mes = next((c for c in df_niver.columns if 'mes' in c.lower() or 'mês' in c.lower()), "Mes")
        
        # Filtra do dia de hoje para frente (no mês atual)
        niver_f = df_niver[(df_niver[c_mes].astype(int) == hoje_br.month) & (df_niver[c_dia].astype(int) >= hoje_br.day)]
        # Se tiver poucos, busca do próximo mês também
        if len(niver_f) < 5:
            prox_m = (hoje_br.month % 12) + 1
            niver_prox = df_niver[df_niver[c_mes].astype(int) == prox_m]
            niver_f = pd.concat([niver_f.sort_values(c_dia), niver_prox.sort_values(c_dia)])
        
        proximos_5 = niver_f.head(5)
        
        if not proximos_5.empty:
            st.markdown("<p style='text-align:center; margin-bottom:5px;'>🎂 <b>Próximos Aniversariantes</b></p>", unsafe_allow_html=True)
            listagem = "<div style='text-align:center; font-size:0.85em; opacity:0.9;'>"
            for _, r in proximos_5.iterrows():
                listagem += f"<span>{r[c_nome]} ({r[c_dia]}/{r[c_mes]})</span> | "
            st.markdown(listagem[:-3] + "</div>", unsafe_allow_html=True)

    # --- Menu Principal ---
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

    # --- RODAPÉ: LOGO, REDES E CONTADOR ---
    st.markdown("<hr style='opacity:0.1;'>", unsafe_allow_html=True)
    
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        if os.path.exists("logo igreja.png"):
            st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("""
        <div class="social-links">
            <a href="https://instagram.com/isosedcosmopolis" target="_blank">Instagram</a>
            <a href="https://youtube.com/@isosedcosmopolis" target="_blank">YouTube</a>
        </div>
    """, unsafe_allow_html=True)

    if 'visitas' not in st.session_state:
        st.session_state.visitas = atualizar_contador()
    
    st.markdown(f"<p class='footer-text'>Visitante nº: {st.session_state.visitas} | ISOSED 2026</p>", unsafe_allow_html=True)

# =========================================================
# --- 4. PÁGINAS COM SEPARAÇÃO POR MESES ---
# =========================================================

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda Mensal</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        df.columns = df.columns.str.lower()
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                if not mes_df.empty:
                    for _, r in mes_df.iterrows():
                        st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos.")

elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Todos os Aniversariantes</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        c_nome = next((c for c in df.columns if 'nome' in c.lower()), "Nome")
        c_dia = next((c for c in df.columns if 'dia' in c.lower()), "Dia")
        c_mes = next((c for c in df.columns if 'mes' in c.lower() or 'mês' in c.lower()), "Mes")
        abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df[c_mes].astype(str) == str(i+1)].sort_values(c_dia)
                if not mes_df.empty:
                    for _, r in mes_df.iterrows():
                        st.write(f"🎁 **Dia {r[c_dia]}** - {r[c_nome]}")
                else: st.info("Sem aniversariantes.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📜 Plano de Leitura</h2>", unsafe_allow_html=True)
    df = carregar_dados("Leitura")
    if not df.empty:
        item = df.iloc[-1]
        st.markdown(f"### {item['Plano']} - Dia {item['Dia']}")
        st.info(f"📍 Referência: {item['Referência']}")
        st.markdown(f'<div style="font-style: italic; color: #ffd700; border-left: 3px solid #ffd700; padding-left: 10px;">{buscar_versiculo(item["Referência"])}</div>', unsafe_allow_html=True)
        st.write(f"**Meditação:** {item['Resumo para meditação']}")

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional</h2>", unsafe_allow_html=True)
    df = carregar_dados("Devocional")
    if not df.empty:
        item = df.iloc[-1]
        st.markdown(f"### {item['titulo']}")
        st.caption(f"📅 {item['data']} | ✨ Tema: {item['tema']}")
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}")
            st.write(f"**Desafio:** {item['desafio']}")

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        for _, r in df[df['dt'].dt.date >= hoje_br].sort_values('dt').iterrows():
            st.markdown(f'<div class="card-isosed"><b>{r["Data"]} ({r["Dia"]})</b><br>{r["Evento"]}: {r["Responsável"]}<br><small>{r["Departamento"]}</small></div>', unsafe_allow_html=True)
