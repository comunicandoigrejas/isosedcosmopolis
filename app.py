import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import re
from datetime import datetime, timedelta
import pytz
import requests
import urllib.parse

# --- 1. FUNÇÕES GLOBAIS (Bíblia e Dados) ---

def buscar_capitulos_divididos(referencia):
    """Busca múltiplos capítulos ou versículos únicos na API"""
    try:
        # Tenta identificar o padrão "Livro X-Y" (Ex: Gênesis 4-7)
        padrao = re.match(r"(.+?)\s+(\d+)-(\d+)", referencia)
        
        if padrao:
            livro = padrao.group(1)
            inicio = int(padrao.group(2))
            fim = int(padrao.group(3))
            
            textos = {}
            for cap in range(inicio, fim + 1):
                ref_cap = f"{livro} {cap}"
                # Ajuste para livros com acentos que a API entende melhor sem
                ref_limpa = ref_cap.replace("Gênesis", "Genesis").replace("Êxodo", "Exodus")
                ref_url = urllib.parse.quote(ref_limpa)
                url = f"https://bible-api.com/{ref_url}?translation=almeida"
                
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    textos[f"Cap. {cap}"] = res.json().get('text', "Texto não encontrado.")
            return textos
        else:
            # Para capítulos únicos ou versículos específicos
            ref_url = urllib.parse.quote(referencia)
            url = f"https://bible-api.com/{ref_url}?translation=almeida"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return {"Leitura": res.json().get('text', "Texto não encontrado.")}
            return {"Erro": f"API erro {res.status_code}"}
    except Exception as e:
        return {"Erro": str(e)}

def buscar_texto_biblico(referencia): # Mantida para compatibilidade
    try:
        ref_url = urllib.parse.quote(referencia)
        url = f"https://bible-api.com/{ref_url}?translation=almeida"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('text', "Texto não encontrado.")
        return f"Erro {response.status_code}"
    except: return "Erro de conexão"

# --- 2. CONFIGURAÇÃO E MEMÓRIA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace(' ', '_') for c in df.columns]
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def conectar_planilha():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open_by_url(URL_PLANILHA)

def salvar_novo_usuario(lista_dados):
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Usuarios") 
        aba.append_row(lista_dados)
        return True
    except: return False

def atualizar_progresso_planilha(usuario, plano, novo_dia):
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Progresso")
        dados = aba.get_all_records()
        df_p = pd.DataFrame(dados)
        if not df_p.empty:
            df_p.columns = [str(c).lower().strip() for c in df_p.columns]
            linha = df_p[(df_p['usuario'] == usuario) & (df_p['plano'] == plano)]
            if not linha.empty:
                idx = linha.index[0] + 2 
                aba.update_cell(idx, 3, int(novo_dia))
                return True
        aba.append_row([usuario, plano, int(novo_dia)])
        return True
    except: return False

# --- 4. ESTILO CSS (Otimizado Mobile) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; font-weight: 800 !important; }
    
    /* Botões do Menu Principal */
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important; height: 60px !important;
        background-color: #0a3d62 !important; border-radius: 12px !important;
        border: 2px solid #3c6382 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }
    button[data-testid="stBaseButton-secondary"] p { color: #FFFFFF !important; font-weight: 900 !important; text-transform: uppercase !important; font-size: 14px !important; }

    /* Ajuste de Abas para scroll horizontal no celular */
    div[data-testid="stTabs"] button { font-size: 14px !important; color: white !important; }
    @media (max-width: 768px) {
        div[data-testid="stTabs"] { overflow-x: auto; white-space: nowrap; }
    }

    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important; border: 2px solid #ffd700 !important;
        border-radius: 15px !important; display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important; margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ROTEADOR DE PÁGINAS ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    # Aniversários da Semana
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
        segunda_proxima = domingo_atual + timedelta(days=8)
        aniv_f = [r for _, r in df_n.iterrows() if domingo_atual <= datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date() <= segunda_proxima]
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)
    
    # Menu Principal em Grade 2x2 para Celular
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))
    
    st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=180)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED 2026</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        abas = st.tabs(meses_nomes)
        for i, aba in enumerate(abas):
            with aba:
                eventos = df[df['data'].dt.month == (i+1)].sort_values(by='data')
                if not eventos.empty:
                    for _, r in eventos.iterrows():
                        st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0a3d62;"><b style="color:#ffd700;">{r["data"].strftime("%d/%m")}</b> - {r["evento"]}</div>', unsafe_allow_html=True)
                else: st.info("Sem eventos.")

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        abas = st.tabs(meses_nomes)
        for i, aba in enumerate(abas):
            with aba:
                lista = df[pd.to_numeric(df['mes']) == (i+1)].sort_values(by='dia')
                if not lista.empty:
                    for _, r in lista.iterrows():
                        st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #f1c40f;"><b style="color:#f1c40f;">Dia {int(r["dia"]):02d}</b> - {r["nome"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Área do Leitor</h1>", unsafe_allow_html=True)
    
    if st.session_state.usuario is None:
        aba_ac = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        with aba_ac[0]:
            l_nome = st.text_input("Nome completo:", key="l_n").strip().title()
            l_senha = st.text_input("Senha:", type="password", key="l_s")
            if st.button("Acessar"):
                df_u = carregar_dados("Usuarios")
                match = df_u[(df_u['nome'] == l_nome) & (df_u['senha'].astype(str) == str(l_senha))]
                if not match.empty:
                    st.session_state.usuario = l_nome
                    st.rerun()
                else: st.error("Erro no login.")
        with aba_ac[1]:
            with st.form("f_cad"):
                n = st.text_input("Nome Completo:")
                tel = st.text_input("WhatsApp:")
                minis = st.selectbox("Ministério:", ["Louvor", "Irmãs", "Jovens", "Varões", "Mídia", "Crianças", "Visitante"])
                nasc = st.date_input("Nascimento:", min_value=datetime(1950, 1, 1), max_value=hoje_br)
                sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Finalizar"):
                    if n and sen:
                        if salvar_novo_usuario([n, tel, minis, str(nasc), sen, 1, "Plano Anual"]): st.success("Sucesso!")
    else:
        u = st.session_state.usuario
        df_l = carregar_dados("Leitura")
        df_progresso = carregar_dados("Progresso")
        if not df_l.empty:
            plano_sel = st.selectbox("Escolha seu Plano:", df_l['plano'].unique())
            dia_p = 1
            if not df_progresso.empty:
                df_progresso.columns = [str(c).lower().strip() for c in df_progresso.columns]
                prog = df_progresso[(df_progresso['usuario'] == u) & (df_progresso['plano'] == plano_sel)]
                if not prog.empty: dia_p = int(prog.iloc[0]['dia_atual'])

            l_hoje = df_l[(df_l['plano'] == plano_sel) & (pd.to_numeric(df_l['dia']) == dia_p)]
            if not l_hoje.empty:
                l = l_hoje.iloc[0]
                ref_hoje = l.get('referencia', '---')
                st.markdown(f"### 📍 {plano_sel} - Dia {dia_p}")
                st.markdown(f'<div style="background:rgba(10,61,98,0.4); padding:20px; border-radius:15px; border-left:5px solid #00b894; margin-bottom:20px;"><h4 style="margin:0; color:#00b894;">📖 Referência:</h4><p style="font-size:1.4em; margin-top:10px;">{ref_hoje}</p></div>', unsafe_allow_html=True)

                # --- BÍBLIA COM ABAS DE CAPÍTULOS ---
                with st.spinner('Abrindo a Bíblia...'):
                    dicionario_textos = buscar_capitulos_divididos(ref_hoje)
                
                if "Erro" not in dicionario_textos:
                    abas_biblia = st.tabs(list(dicionario_textos.keys()))
                    for i, aba_cap in enumerate(abas_biblia):
                        with aba_cap:
                            st.markdown(f'<div style="text-align:justify; line-height:1.8; background:rgba(255,255,255,0.03); padding:15px; border-radius:10px;">{dicionario_textos[list(dicionario_textos.keys())[i]]}</div>', unsafe_allow_html=True)
                
                st.info(f"💡 **Meditação:** {l.get('resumo_para_meditacao', '---')}")
                if st.button("✅ Concluí a leitura!", use_container_width=True):
                    if atualizar_progresso_planilha(u, plano_sel, dia_p + 1):
                        st.balloons()
                        st.rerun()
            else:
                st.success("Plano Concluído!")
                if st.button("Reiniciar"): atualizar_progresso_planilha(u, plano_sel, 1); st.rerun()

        if st.button("Sair da conta"): st.session_state.usuario = None; st.rerun()

# --- PÁGINAS RESTANTES (Escalas, Meditar, Grupos) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas</h1>", unsafe_allow_html=True)
    # ... código original de escalas ...

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    # ... código original de meditar ...

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    # ... código original de grupos ...
