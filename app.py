import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import requests
import calendar

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'user' not in st.session_state: st.session_state.user = None
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p): st.session_state.pagina = p

# --- CSS: CORES, BOTÕES E CAIXAS DE ENTRADA ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    
    /* Texto Geral em Branco */
    p, span, div, label, .stMarkdown { color: white !important; }
    h1, h2, h3, b, strong { color: #ffd700 !important; text-align: center; }

    /* CAIXAS DE TEXTO E ENTRADA (Fundo Azul, Letra Branca) */
    input, textarea, [data-baseweb="select"] > div {
        background-color: #0f3460 !important;
        color: white !important;
        border: 1px solid #ffd700 !important;
    }
    
    /* BOTÕES AZUIS COM FONTE BRANCA */
    div.stButton > button, div.stFormSubmitButton > button {
        width: 100% !important;
        background-color: #0f3460 !important; 
        color: white !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        height: 3.5em !important;
    }
    
    /* CARDS */
    .card-isosed { background: rgba(255, 215, 0, 0.05) !important; border: 1px solid #ffd700 !important; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
    .card-aniv { background: rgba(255, 215, 0, 0.2) !important; border: 1px solid #ffd700 !important; border-radius: 10px; padding: 10px; margin-bottom: 6px; text-align: center; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E APOIO ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
    except: return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            df = pd.DataFrame(aba.get_all_records())
            df.columns = df.columns.str.strip().str.lower()
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline."

def obter_datas_culto_pt(ano, mes):
    dias_pt = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    cal = calendar.Calendar()
    dias_mes = [d for sem in cal.monthdatescalendar(ano, mes) for d in sem if d.month == mes]
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

# =========================================================
# --- ROTEADOR PRINCIPAL ---
# =========================================================

# 1. INÍCIO
if st.session_state.pagina == "Início":
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    df_ag = carregar_dados("Agenda")
    prox = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox} às 18h00</b></div>', unsafe_allow_html=True)

    st.markdown("<h3>🎂 PRÓXIMOS ANIVERSARIANTES</h3>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        n_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in n_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="btn_age")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="btn_ani")
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",), key="btn_ges")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="btn_esc")
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",), key="btn_dev")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="btn_lei")

# 2. AGENDA
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Agenda")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                if not m_df.empty:
                    for _, r in m_df.iterrows(): st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos.")

# 3. ANIVERSÁRIOS
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Aniversariantes")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        c_m = next((c for c in df.columns if 'mes' in c or 'mês' in c), 'mes')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df[c_m].astype(int) == (i+1)].sort_values('dia')
                if not m_df.empty:
                    for _, r in m_df.iterrows(): st.write(f"🎁 Dia {r['dia']} - {r['nome']}")

# 4. DEVOCIONAL (Puxando todas as colunas)
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional</h2>", unsafe_allow_html=True)
    df_dev = carregar_dados("Devocional")
    if not df_dev.empty:
        item = df_dev.iloc[-1]
        st.markdown(f"### {item['titulo']}")
        st.caption(f"📅 {item['data']} | Tema: {item['tema']}")
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}")
            st.write(f"**Desafio:** {item['desafio']}")
    else: st.info("Nenhum devocional cadastrado.")

# 5. GESTÃO (Correção do Form Submit)
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("form_admin"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Acessar Painel"):
                if pw == "ISOSED2026": 
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Incorreto.")
    else:
        st.success("Gestão ISOSED Ativa")
        m = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        tp = st.selectbox("Setor:", ["Fotografia", "Recepção", "Som/Mídia"])
        
        # Correção: O botão de gerar escala agora está DENTRO de um form
        with st.form("form_gerar"):
            if st.form_submit_button(f"Confirmar Geração de {tp}"):
                datas = obter_datas_culto_pt(2026, m)
                sh = conectar_planilha()
                aba = sh.worksheet("Escalas")
                for d in datas:
                    h = "18:00" if d['is_domingo'] else "19:30"
                    aba.append_row([d['data'], d['dia_pt'], h, "Culto", tp, "A definir"])
                st.success("Escala enviada para o Google Sheets!")

# 6. LEITURA (Puxando do Progresso)
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        tab_l, tab_c = st.tabs(["Login", "Novo Cadastro"])
        with tab_l:
            with st.form("form_login_lei"):
                tel = st.text_input("WhatsApp:")
                sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Entrar no Plano"):
                    df_u = carregar_dados("Usuarios")
                    u_f = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                    if not u_f.empty:
                        st.session_state.user = u_f.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Dados incorretos.")
        with tab_c:
            with st.form("form_cad_lei"):
                n = st.text_input("Nome:"); t = st.text_input("WhatsApp:"); s = st.text_input("Senha:", type="password")
                if st.form_submit_button("Criar Conta"):
                    sh = conectar_planilha()
                    sh.worksheet("Usuarios").append_row([n, t, "Membro", "", s, 1, "Anual 2026"])
                    sh.worksheet("Progresso").append_row([t, "Anual 2026", 1])
                    st.success("Conta criada! Faça login.")
    else:
        # LOGADO: Puxa o dia da aba Progresso
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        p_row = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        
        if not p_row.empty:
            dia_atual = int(p_row.iloc[0]['dia_atual'])
            st.markdown(f"### Olá, {u['nome']}! 📖")
            st.markdown(f"<div class='card-isosed'>Você está no <b>Dia {dia_atual}</b></div>", unsafe_allow_html=True)
            
            df_lei = carregar_dados("Leitura")
            l_hoje = df_lei[df_lei['dia'].astype(str) == str(dia_atual)]
            
            if not l_hoje.empty:
                l = l_hoje.iloc[0]
                st.info(f"📍 Referência: {l['referência']}")
                st.markdown(f'<div style="color:#ffd700; font-style:italic;">{buscar_versiculo(l["referência"])}</div>', unsafe_allow_html=True)
                st.write(f"**Meditação:** {l['resumo para meditação']}")
                
                if st.button("✅ Marcar como Lido"):
                    sh = conectar_planilha()
                    aba_p = sh.worksheet("Progresso")
                    cell = aba_p.find(str(u['telefone']))
                    aba_p.update_cell(cell.row, 3, dia_atual + 1)
                    st.rerun()
            else: st.warning("Leitura não encontrada para este dia.")
        else: st.error("Erro ao localizar seu progresso.")
