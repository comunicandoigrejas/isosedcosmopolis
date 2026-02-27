import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
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
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E DADOS ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # ID DA SUA PLANILHA
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

# =========================================================
# --- ROTEADOR PRINCIPAL ---
# =========================================================

# --- GAVETA 1: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Santa Ceia Dinâmica
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox_ceia = ceia.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.4em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # Aniversariantes do Mês (Destaque Amarelo)
    st.markdown("<p style='text-align:center; font-weight:bold;'>🎂 PRÓXIMOS ANIVERSARIANTES</p>", unsafe_allow_html=True)
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c or 'mês' in c), 'mes')
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        for _, r in niver_f.iterrows():
            st.markdown(f'<div class="card-aniv">🎂 {r["nome"]} - Dia {r["dia"]}</div>', unsafe_allow_html=True)

    # Menu Principal
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

# --- GAVETA 2: AGENDA (MESES SEPARADOS) ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda Mensal 2026</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                if not m_df.empty:
                    for _, r in m_df.iterrows(): st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos cadastrados.")

# --- GAVETA 3: ANIVERSÁRIOS (MESES SEPARADOS) ---
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Todos os Aniversariantes</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        col_m = next((c for c in df.columns if 'mes' in c or 'mês' in c), 'mes')
        for i, aba in enumerate(abas):
            with aba:
                m_df = df[df[col_m].astype(int) == (i+1)].sort_values('dia')
                if not m_df.empty:
                    for _, r in m_df.iterrows(): st.write(f"🎁 **Dia {r['dia']}** - {r['nome']}")
                else: st.info("Ninguém este mês.")

# --- GAVETA 4: LEITURA (FIX DO INDEXERROR) ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        t1, t2 = st.tabs(["Login", "Cadastro"])
        with t1:
            with st.form("l"):
                f_tel = st.text_input("WhatsApp:")
                f_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Acessar"):
                    df_u = carregar_dados("Usuarios")
                    u_find = df_u[(df_u['telefone'].astype(str) == str(f_tel)) & (df_u['senha'].astype(str) == str(f_sen))]
                    if not u_find.empty:
                        st.session_state.user = u_find.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Dados incorretos!")
        with t2:
            with st.form("c"):
                c_nom = st.text_input("Nome:")
                c_tel = st.text_input("WhatsApp:")
                c_min = st.text_input("Ministério:")
                c_nas = st.text_input("Nascimento:")
                c_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Cadastrar"):
                    sh = conectar_planilha()
                    sh.worksheet("Usuarios").append_row([c_nom, c_tel, c_min, c_nas, c_sen, 1, "Anual 2026"])
                    sh.worksheet("Progresso").append_row([c_tel, "Anual 2026", 1])
                    st.success("Conta criada! Entre agora.")
    else:
        # LOGADO: Proteção contra IndexError
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        user_p = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        
        if user_p.empty: # Caso o registro no progresso tenha sumido, cria um novo
            sh = conectar_planilha()
            sh.worksheet("Progresso").append_row([u['telefone'], "Anual 2026", 1])
            dia_atual = 1
        else:
            dia_atual = int(user_p.iloc[0]['dia_atual'])
            
        st.markdown(f"### Olá, {u['nome']}! Dia {dia_atual}")
        df_lei = carregar_dados("Leitura")
        l = df_lei[df_lei['dia'].astype(str) == str(dia_atual)]
        if not l.empty:
            item = l.iloc[0]
            st.info(f"📍 {item['referência']}")
            st.write(buscar_versiculo(item['referência']))
            if st.button("✅ Concluir"):
                sh = conectar_planilha()
                aba = sh.worksheet("Progresso")
                cell = aba.find(str(u['telefone']))
                aba.update_cell(cell.row, 3, dia_atual + 1)
                st.rerun()

# --- FUNÇÕES DE APOIO PARA GERAÇÃO ---
def obter_datas_culto(ano, mes):
    cal = calendar.Calendar()
    dias_mes = [d for sem in cal.monthdatescalendar(ano, mes) for d in sem if d.month == mes]
    
    # Filtra Quartas (2), Sextas (4), Domingos (6)
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    
    # Encontra o último sábado do mês
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados:
        datas.append(max(sabados))
    
    return sorted(datas)

# =========================================================
# --- PÁGINA: GESTÃO (COM GERADOR REAL) ---
# =========================================================
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    
    if not st.session_state.admin_ok:
        with st.form("adm_login"):
            pw = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("Liberar Painel"):
                if pw == "ISOSED2026": 
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha Incorreta!")
    else:
        st.markdown("<h2>⚙️ Painel de Gestão ISOSED</h2>", unsafe_allow_html=True)
        t_view, t_gen = st.tabs(["📊 Estatísticas", "🤖 Gerar Novas Escalas"])
        
        with t_view:
            df_u = carregar_dados("Usuarios")
            st.metric("Membros Cadastrados", len(df_u))
            st.dataframe(df_u, use_container_width=True)
            
        with t_gen:
            st.write("Selecione o período para criar o rodízio:")
            c1, c2 = st.columns(2)
            mes_sel = c1.selectbox("Mês:", list(range(1,13)), index=hoje_br.month - 1)
            ano_sel = c2.number_input("Ano:", value=2026)
            
            tipo_escala = st.radio("Qual escala deseja gerar?", ["🤝 Recepção", "📸 Fotografia", "🔊 Som/Mídia"])
            
            if st.button(f"Gerar e Salvar Escala de {tipo_escala}"):
                with st.spinner("Calculando rodízio..."):
                    datas = obter_datas_culto(ano_sel, mes_sel)
                    sh = conectar_planilha()
                    aba_e = sh.worksheet("Escalas")
                    novas_linhas = []
                    
                    # --- LÓGICA DE RECEPÇÃO (Duplas) ---
                    if "Recepção" in tipo_escala:
                        equipe = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                        idx = 0
                        for d in datas:
                            p1, p2 = equipe[idx % 7], equipe[(idx + 1) % 7]
                            h = "18h00" if d.weekday()==6 else "19h30"
                            novas_linhas.append([d.strftime('%d/%m/%Y'), calendar.day_name[d.weekday()], h, "Culto", "Recepção", f"{p1} e {p2}"])
                            idx += 2
                    
                    # --- LÓGICA DE FOTOGRAFIA ---
                    elif "Fotografia" in tipo_escala:
                        equipe = ["Tiago", "Grazi"]
                        for i, d in enumerate(datas):
                            h = "18h00" if d.weekday()==6 else "19h30"
                            novas_linhas.append([d.strftime('%d/%m/%Y'), calendar.day_name[d.weekday()], h, "Culto", "Fotografia", equipe[i % 2]])
                    
                    # --- LÓGICA DE SOM/MÍDIA (Regra do Júnior) ---
                    elif "Som" in tipo_escala:
                        pg = ["Lucas", "Samuel", "Nicholas"]
                        pdom = ["Júnior", "Lucas", "Samuel", "Nicholas"]
                        ig, idom = 0, 0
                        for d in datas:
                            h = "18h00" if d.weekday()==6 else "19h30"
                            op = pdom[idom % 4] if d.weekday()==6 else pg[ig % 3]
                            novas_linhas.append([d.strftime('%d/%m/%Y'), calendar.day_name[d.weekday()], h, "Culto", "Mídia", op])
                            if d.weekday()==6: idom += 1
                            else: ig += 1
                    
                    # Salva tudo de uma vez para ser mais rápido
                    if novas_linhas:
                        for linha in novas_linhas:
                            aba_e.append_row(linha)
                        st.success(f"✅ Escala de {tipo_escala} para o mês {mes_sel} gerada com sucesso!")
                    else:
                        st.error("Erro ao gerar datas.")

# (Lembre-se de manter o restante do código com as abas Início, Leitura, etc.)

# --- GAVETAS RESTANTES (ESCALAS E DEVOCIONAL) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Escalas")
    t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som", "🤝 Recepção"])
    if not df.empty:
        for t, dep in zip([t1, t2, t3], ["Foto", "Mídia", "Recepção"]):
            with t:
                f = df[df['departamento'].str.contains(dep, case=False, na=False)]
                for _, r in f.iterrows():
                    st.markdown(f'<div class="card-isosed"><b>{r["data"]}</b> - {r["responsável"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Devocional")
    if not df.empty:
        i = df.iloc[-1]
        st.markdown(f"### {i['titulo']}")
        st.write(i['texto'])
