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

# --- 2. FUNÇÕES DE CONEXÃO E BÍBLIA ---
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
            df.columns = df.columns.str.strip()
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

def buscar_versiculo(ref):
    try:
        r = requests.get(f"https://bible-api.com/{ref}?translation=almeida")
        return r.json()['text'] if r.status_code == 200 else "Referência não encontrada."
    except: return "Bíblia indisponível."

# --- 3. LÓGICA DE USUÁRIO (LOGIN/CADASTRO) ---
def gerenciar_acesso(dados_user, acao="login"):
    sh = conectar_planilha()
    if not sh: return False, "Erro de conexão"
    
    aba_user = sh.worksheet("Usuarios")
    aba_prog = sh.worksheet("Progresso")
    
    if acao == "cadastro":
        # nome, telefone, ministerio, nascimento, senha, dia_atual, plano_escolhido
        aba_user.append_row(list(dados_user.values()))
        # usuario (telefone), plano, dia_atual
        aba_prog.append_row([dados_user['telefone'], dados_user['plano_escolhido'], 1])
        return True, "Cadastro realizado com sucesso!"
    
    else: # LOGIN
        df_u = pd.DataFrame(aba_user.get_all_records())
        user = df_u[(df_u['telefone'].astype(str) == str(dados_user['telefone'])) & 
                    (df_u['senha'].astype(str) == str(dados_user['senha']))]
        if not user.empty:
            return True, user.iloc[0].to_dict()
        return False, "Telefone ou senha incorretos."

# =========================================================
# --- PÁGINA: INÍCIO ---
# =========================================================
if st.session_state.pagina == "Início":
    st.markdown("<h3>⛪ ISOSED COSMÓPOLIS</h3>", unsafe_allow_html=True)
    
    # 🍇 Santa Ceia Dinâmica
    df_ag = carregar_dados("Agenda")
    prox_ceia = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceias = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)]
        c_fut = ceias[ceias['dt_p'].dt.date >= hoje_br].sort_values('dt_p')
        if not c_fut.empty: prox_ceia = c_fut.iloc[0]['data']

    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em;">{prox_ceia} às 18h00</b></div>', unsafe_allow_html=True)

    # 🎂 Próximos 5 Aniversariantes
    df_nv = carregar_dados("Aniversariantes")
    if not df_nv.empty:
        col_m = next((c for c in df_nv.columns if 'mes' in c.lower() or 'mês' in c.lower()), "Mes")
        col_d = next((c for c in df_nv.columns if 'dia' in c.lower()), "Dia")
        niver_f = df_nv[(df_nv[col_m].astype(int) == hoje_br.month) & (df_nv[col_d].astype(int) >= hoje_br.day)].sort_values(col_d).head(5)
        if not niver_f.empty:
            list_n = " | ".join([f"{r['Nome']} ({r[col_d]})" for _, r in niver_f.iterrows()])
            st.markdown(f"<p style='text-align:center; font-size:0.8em;'>🎂 <b>Próximos:</b> {list_n}</p>", unsafe_allow_html=True)

    # Menu
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

    # Rodapé
    st.markdown("<hr style='opacity:0.1;'>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    st.markdown("<div style='text-align:center;'><a href='#' style='color:#ffd700;'>Instagram</a> | <a href='#' style='color:#ffd700;'>YouTube</a></div>", unsafe_allow_html=True)

# =========================================================
# --- PÁGINA: LEITURA (COM CADASTRO E PROGRESSO) ---
# =========================================================
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    
    if st.session_state.user is None:
        st.markdown("<h2>📖 Plano de Leitura</h2>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Entrar", "Criar Conta"])
        
        with t1:
            with st.form("login"):
                f_tel = st.text_input("WhatsApp (com DDD):")
                f_sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Acessar meu Plano"):
                    ok, res = gerenciar_acesso({"telefone": f_tel, "senha": f_sen}, "login")
                    if ok:
                        st.session_state.user = res
                        st.rerun()
                    else: st.error(res)
        
        with t2:
            with st.form("cadastro"):
                c_nom = st.text_input("Nome Completo:")
                c_tel = st.text_input("WhatsApp:")
                c_min = st.selectbox("Ministério:", ["Membro", "Mídia", "Recepção", "Louvor", "Infantil", "Liderança"])
                c_nas = st.text_input("Data Nascimento (DD/MM):")
                c_sen = st.text_input("Crie uma Senha:", type="password")
                c_pla = st.selectbox("Escolha seu Plano:", ["Anual 2026", "Novo Testamento", "Casais"])
                if st.form_submit_button("Cadastrar e Iniciar"):
                    new_u = {"nome": c_nom, "telefone": c_tel, "ministerio": c_min, "nascimento": c_nas, "senha": c_sen, "dia_atual": 1, "plano_escolhido": c_pla}
                    ok, msg = gerenciar_acesso(new_u, "cadastro")
                    if ok: st.success(msg)
                    else: st.error(msg)
    
    else:
        # Usuário Logado - Mostrar Progresso
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        # Busca o dia_atual do usuário na aba Progresso
        user_p = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        dia_hoje = user_p.iloc[0]['dia_atual'] if not user_p.empty else 1
        
        st.markdown(f"### Olá, {u['nome']}! ✨")
        st.markdown(f"<div class='card-isosed'>📅 Você está no <b>Dia {dia_hoje}</b> do plano <b>{u['plano_escolhido']}</b></div>", unsafe_allow_html=True)
        
        # Busca a leitura correspondente ao dia
        df_lei = carregar_dados("Leitura")
        leitura_dia = df_lei[df_lei['Dia'].astype(int) == int(dia_hoje)]
        
        if not leitura_dia.empty:
            l = leitura_dia.iloc[0]
            st.info(f"📍 Referência: {l['Referência']}")
            st.markdown(f'<div class="texto-biblico">{buscar_versiculo(l["Referência"])}</div>', unsafe_allow_html=True)
            st.write(f"**Meditação:** {l['Resumo para meditação']}")
            
            if st.button("✅ Marcar como Lido e Avançar"):
                sh = conectar_planilha()
                aba_p = sh.worksheet("Progresso")
                # Encontra a linha do usuário (busca por telefone)
                celula = aba_p.find(str(u['telefone']))
                novo_dia = int(dia_hoje) + 1
                aba_p.update_cell(celula.row, 3, novo_dia) # Coluna 3 é dia_atual
                st.success("Parabéns! Progresso salvo.")
                st.rerun()
        
        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()

# (Repetir lógica de ELIF para Agenda, Aniv, Escalas e Devocional conforme versões anteriores)
