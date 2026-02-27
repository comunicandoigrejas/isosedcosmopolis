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

def navegar(p): st.session_state.pagina = p

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
    .texto-biblico { font-style: italic; color: #ffd700; border-left: 3px solid #ffd700; padding-left: 10px; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E LIMPEZA (ANTI-ERRO) ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        # --- COLE SEU ID AQUI ---
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
            # Limpeza mestre: Remove espaços e deixa tudo minúsculo para busca interna
            df.columns = df.columns.str.strip().str.lower()
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
    except: return "Bíblia offline."

# =========================================================
# --- 3. PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # --- SANTA CEIA DINÂMICA ---
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceias = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)]
        c_fut = ceias[ceias['dt_p'].dt.date >= hoje_br].sort_values('dt_p')
        if not c_fut.empty: prox_ceia = c_fut.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # --- PRÓXIMOS 5 ANIVERSARIANTES ---
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        # Pega do dia atual até o fim do mês
        niver_f = df_nv[(df_nv['mes'].astype(int) == hoje_br.month) & (df_nv['dia'].astype(int) >= hoje_br.day)].sort_values('dia').head(5)
        if not niver_f.empty:
            st.markdown("<p style='text-align:center; margin-bottom:5px;'>🎂 <b>Próximos Aniversariantes</b></p>", unsafe_allow_html=True)
            # Como limpamos as colunas, usamos 'nome' e 'dia' minúsculos
            list_n = " | ".join([f"{r['nome']} ({r['dia']})" for _, r in niver_f.iterrows()])
            st.markdown(f"<div style='text-align:center; font-size:0.8em; opacity:0.8;'>{list_n}</div>", unsafe_allow_html=True)

    # --- MENU PRINCIPAL ---
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
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    fl1, fl2, fl3 = st.columns([1, 1.2, 1])
    with fl2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    
    st.markdown("""
        <div style="text-align:center; margin:10px 0;">
            <a href="https://instagram.com/isosedcosmopolis" target="_blank" style="color:#ffd700; text-decoration:none; margin:0 10px;">📸 Instagram</a>
            <a href="https://youtube.com/@isosedcosmopolis" target="_blank" style="color:#ffd700; text-decoration:none; margin:0 10px;">🎥 YouTube</a>
        </div>
    """, unsafe_allow_html=True)

    if 'visitas' not in st.session_state: st.session_state.visitas = atualizar_contador()
    st.markdown(f"<p style='text-align:center; opacity:0.4; font-size:0.7em;'>Visitante nº: {st.session_state.visitas} | ISOSED 2026</p>", unsafe_allow_html=True)

# =========================================================
# --- PÁGINA: LEITURA (LOGIN E PROGRESSO) ---
# =========================================================
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    
    if st.session_state.user is None:
        st.markdown("<h2>🔑 Acesse seu Plano</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Fazer Login", "Criar Conta"])
        
        with t1:
            with st.form("login_form"):
                f_tel = st.text_input("WhatsApp (com DDD):")
                f_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Entrar"):
                    df_u = carregar_dados("Usuarios")
                    u_find = df_u[(df_u['telefone'].astype(str) == str(f_tel)) & (df_u['senha'].astype(str) == str(f_sen))]
                    if not u_find.empty:
                        st.session_state.user = u_find.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Dados incorretos.")
        
        with t2:
            with st.form("cad_form"):
                st.write("Novo por aqui? Cadastre-se!")
                c_nom = st.text_input("Nome:")
                c_tel = st.text_input("WhatsApp:")
                c_sen = st.text_input("Crie uma Senha:", type="password")
                c_min = st.text_input("Ministério:")
                c_nas = st.text_input("Nascimento (DD/MM):")
                if st.form_submit_button("Começar Plano"):
                    sh = conectar_planilha()
                    aba_u = sh.worksheet("Usuarios")
                    aba_p = sh.worksheet("Progresso")
                    # nome, telefone, ministerio, nascimento, senha, dia_atual, plano_escolhido
                    aba_u.append_row([c_nom, c_tel, c_min, c_nas, c_sen, 1, "Anual 2026"])
                    aba_p.append_row([c_tel, "Anual 2026", 1])
                    st.success("Conta criada! Agora faça o login.")

    else:
        # Logado: Mostra o dia da leitura baseado na aba Progresso
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        p_row = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        dia_atual = p_row.iloc[0]['dia_atual'] if not p_row.empty else 1
        
        st.markdown(f"### Olá, {u['nome']}! 📖")
        st.markdown(f"<div class='card-isosed'>Você está no <b>Dia {dia_atual}</b> do seu plano.</div>", unsafe_allow_html=True)
        
        df_lei = carregar_dados("Leitura")
        # Filtra pelo dia exato do progresso do usuário
        l_hoje = df_lei[df_lei['dia'].astype(str) == str(dia_atual)]
        
        if not l_hoje.empty:
            l = l_hoje.iloc[0]
            st.info(f"📍 Referência: {l['referência']}")
            st.markdown(f'<div class="texto-biblico">{buscar_versiculo(l["referência"])}</div>', unsafe_allow_html=True)
            st.write(f"**Meditação:** {l['resumo para meditação']}")
            
            if st.button("✅ Concluir Leitura e Avançar"):
                sh = conectar_planilha()
                aba_p = sh.worksheet("Progresso")
                cell = aba_p.find(str(u['telefone']))
                aba_p.update_cell(cell.row, 3, int(dia_atual) + 1)
                st.success("Progresso salvo! Até amanhã!")
                st.rerun()
        else:
            st.warning("Plano concluído ou conteúdo não cadastrado para este dia.")

        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()

# --- 4. PÁGINAS MENSAIS (AGENDA E ANIV) ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🗓️ Agenda ISOSED</h2>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df['dt'].dt.month == (i+1)].sort_values('dt')
                if not mes_df.empty:
                    for _, r in mes_df.iterrows(): st.write(f"**{r['dt'].strftime('%d/%m')}** - {r['evento']}")
                else: st.info("Sem eventos.")

elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>🎂 Todos os Aniversariantes</h2>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    abas = st.tabs([calendar.month_name[i].capitalize()[:3] for i in range(1,13)])
    if not df.empty:
        for i, aba in enumerate(abas):
            with aba:
                mes_df = df[df['mes'].astype(int) == (i+1)].sort_values('dia')
                if not mes_df.empty:
                    for _, r in mes_df.iterrows(): st.write(f"🎁 **Dia {r['dia']}** - {r['nome']}")
                else: st.info("Sem aniversariantes.")

# --- 5. DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📖 Devocional</h2>", unsafe_allow_html=True)
    df = carregar_dados("Devocional")
    if not df.empty:
        item = df.iloc[-1]
        st.markdown(f"### {item['titulo']}")
        st.success(f"📖 Versículo: {item['versiculo']}")
        st.write(item['texto'])
        with st.expander("🎯 Aplicação & Desafio"):
            st.write(f"**Aplicação:** {item['aplicacao']}")
            st.write(f"**Desafio:** {item['desafio']}")

# --- 6. ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df = carregar_dados("Escalas")
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        for _, r in df[df['dt'].dt.date >= hoje_br].sort_values('dt').iterrows():
            st.markdown(f'<div class="card-isosed"><b>{r["data"]}</b> - {r["evento"]}<br>👤 {r["responsável"]} ({r["departamento"]})</div>', unsafe_allow_html=True)
