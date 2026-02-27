import streamlit as st
import pandas as pd
from datetime import datetime, date
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

st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    .card-isosed { background: rgba(255, 215, 0, 0.08) !important; border: 1px solid #ffd700 !important; border-radius: 12px; padding: 15px; margin-bottom: 15px; }
    .card-aniv { background: rgba(255, 215, 0, 0.2) !important; border: 2px solid #ffd700 !important; border-radius: 10px; padding: 10px; margin-bottom: 8px; text-align: center; color: #ffd700 !important; font-weight: bold; }
    .stButton>button { width: 100% !important; background-color: #0f3460 !important; color: white !important; border-radius: 10px !important; font-weight: bold; height: 3.5em; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; }
    .texto-biblico { font-style: italic; color: #ffd700; border-left: 3px solid #ffd700; padding-left: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES DE CONEXÃO E TRADUÇÃO ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open_by_key("1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0")
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

def obter_datas_culto_pt(ano, mes):
    dias_pt = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
    cal = calendar.Calendar()
    dias_mes = [d for sem in cal.monthdatescalendar(ano, mes) for d in sem if d.month == mes]
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    
    # Retorna DICTIONARY para evitar o TypeError
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia offline."

# =========================================================
# --- ROTEADOR PRINCIPAL (TODOS OS ELIF ALINHADOS) ---
# =========================================================

# --- 1. INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox_ceia = ceia.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.4em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; font-weight:bold;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in niver_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

# --- 2. AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda Mensal</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                for _, r in m_df.iterrows(): st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")

# --- 3. ANIVERSÁRIOS ---
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Aniversariantes do Ano</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        col_m = next((c for c in df.columns if 'mes' in c or 'mês' in c), 'mes')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df[col_m].astype(int) == (i+1)].sort_values('dia')
                for _, r in m_df.iterrows(): st.write(f"🎁 **Dia {r['dia']}** - {r['nome']}")

# --- 4. GESTÃO (FIX DO TYPEERROR) ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if not st.session_state.admin_ok:
        with st.form("adm"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Liberar"):
                if pw == "ISOSED2026": st.session_state.admin_ok = True; st.rerun()
                else: st.error("Incorreto!")
    else:
        st.markdown("<h2>⚙️ Painel de Gestão</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Membros", "Gerar Escalas"])
        with t1: st.dataframe(carregar_dados("Usuarios"))
        with t2:
            m = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
            tp = st.selectbox("Setor:", ["Fotografia", "Recepção", "Som/Mídia"])
            if st.button("Gerar Escala"):
                datas_culto = obter_datas_culto_pt(2026, m) # Agora retorna lista de DICIONÁRIOS
                sh = conectar_planilha()
                aba = sh.worksheet("Escalas")
                
                if tp == "Fotografia":
                    eq = ["Tiago", "Grazi"]
                    for i, d in enumerate(datas_culto):
                        resp = eq[i % 2]
                        hor = "18:00" if d['is_domingo'] else "19:30"
                        aba.append_row([d['data'], d['dia_pt'], hor, "Culto", "Fotografia", resp])
                
                elif tp == "Recepção":
                    eq = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                    idx = 0
                    for d in datas_culto:
                        resp = f"{eq[idx % 7]} e {eq[(idx+1) % 7]}"
                        hor = "18:00" if d['is_domingo'] else "19:30"
                        aba.append_row([d['data'], d['dia_pt'], hor, "Culto", "Recepção", resp])
                        idx += 2
                st.success("✅ Escala gerada!")

# --- 5. LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        t1, t2 = st.tabs(["Entrar", "Criar Conta"])
        with t1:
            with st.form("l"):
                tel = st.text_input("WhatsApp:"); sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Acessar"):
                    df_u = carregar_dados("Usuarios")
                    u_f = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                    if not u_f.empty: st.session_state.user = u_f.iloc[0].to_dict(); st.rerun()
        with t2:
            with st.form("c"):
                n = st.text_input("Nome:"); t = st.text_input("Tel:"); m = st.text_input("Min:"); na = st.text_input("Nasc:"); s = st.text_input("Senha:", type="password")
                if st.form_submit_button("Cadastrar"):
                    sh = conectar_planilha(); sh.worksheet("Usuarios").append_row([n, t, m, na, s, 1, "Anual 2026"])
                    sh.worksheet("Progresso").append_row([t, "Anual 2026", 1]); st.success("OK! Faça Login.")
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        p_row = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        dia = int(p_row.iloc[0]['dia_atual']) if not p_row.empty else 1
        st.markdown(f"### Olá, {u['nome']}! Dia {dia}")
        df_l = carregar_dados("Leitura")
        l_h = df_l[df_l['dia'].astype(str) == str(dia)]
        if not l_h.empty:
            l = l_h.iloc[0]; st.info(f"📍 {l['referência']}"); st.write(buscar_versiculo(l['referência']))
            if st.button("✅ Concluir"):
                sh = conectar_planilha(); cell = sh.worksheet("Progresso").find(str(u['telefone']))
                sh.worksheet("Progresso").update_cell(cell.row, 3, dia + 1); st.rerun()

# --- 6. ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Escalas")
    t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som", "🤝 Recepção"])
    if not df.empty:
        for t, dep in zip([t1, t2, t3], ["Foto", "Mídia", "Recepção"]):
            with t:
                f = df[df['departamento'].str.contains(dep, case=False, na=False)]
                for _, r in f.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]}</b> - {r["responsável"]}</div>', unsafe_allow_html=True)

# --- 7. DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Devocional")
    if not df.empty:
        i = df.iloc[-1]; st.markdown(f"### {i['titulo']}"); st.write(i['texto'])
