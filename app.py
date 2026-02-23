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

# --- 1. FUNÇÕES GLOBAIS ---
def contabilizar_acesso():
    """Lê o valor atual na planilha e soma +1 a cada nova sessão"""
    if 'acesso_registrado' not in st.session_state:
        try:
            sh = conectar_planilha()
            aba = sh.worksheet("Acessos")
            valor_atual = int(aba.acell('A2').value)
            novo_valor = valor_atual + 1
            aba.update_cell(2, 1, novo_valor)
            st.session_state.acesso_registrado = True
            return novo_valor
        except:
            return "---"
    else:
        # Se já contou nesta sessão, apenas busca o valor da planilha sem somar
        try:
            sh = conectar_planilha()
            aba = sh.worksheet("Acessos")
            return aba.acell('A2').value
        except: return "---"

# Chame a função logo no início para carregar o número
total_acessos = contabilizar_acesso()
def buscar_capitulos_divididos(referencia):
    try:
        padrao = re.match(r"(.+?)\s+(\d+)-(\d+)", referencia)
        if padrao:
            livro = padrao.group(1)
            inicio, fim = int(padrao.group(2)), int(padrao.group(3))
            textos = {}
            for cap in range(inicio, fim + 1):
                ref_cap = f"{livro} {cap}"
                ref_limpa = ref_cap.replace("Gênesis", "Genesis").replace("Êxodo", "Exodus")
                ref_url = urllib.parse.quote(ref_limpa)
                url = f"https://bible-api.com/{ref_url}?translation=almeida"
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    textos[f"Cap. {cap}"] = res.json().get('text', "Texto não encontrado.")
            return textos
        else:
            ref_url = urllib.parse.quote(referencia)
            url = f"https://bible-api.com/{ref_url}?translation=almeida"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return {"Leitura": res.json().get('text', "Texto não encontrado.")}
            return {"Erro": "Não encontrado."}
    except: return {"Erro": "Erro de conexão."}

def buscar_texto_biblico(referencia):
    try:
        ref_url = urllib.parse.quote(referencia)
        res = requests.get(f"https://bible-api.com/{ref_url}?translation=almeida", timeout=10)
        return res.json().get('text', "...") if res.status_code == 200 else "..."
    except: return "..."

# --- 2. CONFIGURAÇÃO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'usuario' not in st.session_state: st.session_state.usuario = None

def navegar(p): st.session_state.pagina = p

# --- 3. BANCO DE DADOS ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_p = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_p}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normalização de colunas para bater com o código
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace(' ', '_') for c in df.columns]
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

def conectar_planilha():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
    return gspread.authorize(creds).open_by_url(URL_PLANILHA)

def salvar_novo_usuario(lista):
    try:
        conectar_planilha().worksheet("Usuarios").append_row(lista)
        return True
    except: return False

def atualizar_progresso_planilha(u, p, d):
    try:
        aba = conectar_planilha().worksheet("Progresso")
        df_p = pd.DataFrame(aba.get_all_records())
        if not df_p.empty:
            df_p.columns = [str(c).lower().strip() for c in df_p.columns]
            linha = df_p[(df_p['usuario'] == u) & (df_p['plano'] == p)]
            if not linha.empty:
                aba.update_cell(linha.index[0] + 2, 3, int(d))
                return True
        aba.append_row([u, p, int(d)])
        return True
    except: return False

# --- 4. CSS ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, p { color: #FFFFFF !important; font-weight: 800 !important; }
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important; height: 60px !important;
        background-color: #0a3d62 !important; border-radius: 12px !important;
        border: 2px solid #3c6382 !important;
    }
    button[data-testid="stBaseButton-secondary"] p { font-weight: 900 !important; text-transform: uppercase !important; font-size: 14px !important; }
    .card-niver { background: rgba(255,215,0,0.1); border: 2px solid #ffd700; border-radius: 15px; padding: 10px; text-align: center; }
    div[data-testid="stTabs"] { overflow-x: auto; white-space: nowrap; }
    /* Rodapé Fixo das Redes Sociais */
    .footer-social {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0a3d62;
        padding: 10px 0;
        text-align: center;
        border-top: 2px solid #3c6382;
        z-index: 999;
    }
    .footer-social a {
        color: white !important;
        text-decoration: none;
        margin: 0 15px;
        font-weight: bold;
        font-size: 1.1em;
    }
    /* Cartão de Horários de Culto */
    .culto-card {
        background: rgba(10, 61, 98, 0.4);
        border: 1px solid #3c6382;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
    .culto-item {
        display: flex;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. ROTEADOR ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    # Horários de Culto
    st.markdown("""
        <div class="culto-card">
            <h4 style="margin:0; color:#ffd700; text-align:center;">🙏 Nossos Cultos</h4>
            <div class="culto-item"><span>Segunda-feira</span> <b>Oração Ministerial</b></div>
            <div class="culto-item"><span>Quarta-feira</span> <b>Culto de Ensino - 19h30</b></div>
            <div class="culto-item"><span>Sexta-feira</span> <b>Culto de Libertação - 19h30</b></div>
            <div class="culto-item"><span>Domingo</span> <b>Culto da Família - 18h00</b></div>
        </div>
    """, unsafe_allow_html=True)

    # Menu Principal 2x2
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), use_container_width=True)
        st.button("👥 Grupos", on_click=navegar, args=("Grupos",), use_container_width=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",), use_container_width=True)
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), use_container_width=True)
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), use_container_width=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), use_container_width=True)

    # Logo e Contador
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"):
        col_esq, col_centro, col_dir = st.columns([1, 2, 1])
        with col_centro:
            st.image("logo igreja.png", use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-size:0.8em; opacity:0.7;'>Total de acessos: {total_acessos}</p>", unsafe_allow_html=True)
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
        for i, aba in enumerate(abas):
            with aba:
                evs = df[df['data'].dt.month == (i+1)].sort_values(by='data')
                if not evs.empty:
                    for _, r in evs.iterrows():
                        st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid #0a3d62;"><b style="color:#ffd700;">{r["data"].strftime("%d/%m")}</b> - {r["evento"]}</div>', unsafe_allow_html=True)
                else: st.info("Sem eventos.")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos e Departamentos</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        deptos = ["Jovens", "Varões", "Irmãs", "Louvor", "Missões", "Tarde com Deus"]
        abas = st.tabs(deptos)
        for i, depto in enumerate(abas):
            with depto:
                f = df[df['evento'].str.contains(deptos[i], case=False, na=False)].sort_values(by='data')
                if not f.empty:
                    for _, r in f.iterrows():
                        st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:10px; margin-bottom:8px; border-left:5px solid #00b894;"><b style="color:#00b894;">{r["data"].strftime("%d/%m/%Y")}</b> — {r["evento"]}</div>', unsafe_allow_html=True)
                else: st.info(f"Sem datas para {deptos[i]}.")

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes</h1>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
        for i, aba in enumerate(abas):
            with aba:
                l = df[pd.to_numeric(df['mes'], errors='coerce') == (i+1)].sort_values(by='dia')
                for _, r in l.iterrows():
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid #f1c40f;"><b style="color:#f1c40f;">Dia {int(r["dia"]):02d}</b> - {r["nome"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df_m = carregar_dados("Midia")
        if not df_m.empty:
            for _, r in df_m.iterrows():
                with st.expander(f"📅 {r.get('data','')} - {r.get('culto','')}"):
                    st.write(f"**Operador:** {r.get('op','')} | **Foto:** {r.get('foto','')} | **Chegada:** {r.get('chegada','')}")
    with t2:
        df_r = carregar_dados("Recepcao")
        if not df_r.empty:
            for _, r in df_r.iterrows():
                with st.expander(f"📅 {r.get('data','')} ({r.get('dia','')})"):
                    st.write(f"**Dupla:** {r.get('dupla','')} | **Chegada:** {r.get('chegada','')}")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        hj = df[df["data"].astype(str).str.strip() == d_sel.strftime('%d/%m/%Y')]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"**Tema:** {d.get('tema', '')}")
            st.markdown(f"### {d.get('titulo', '')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', ''))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', ''))
        else: st.warning("Sem devocional para hoje.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Área do Leitor</h1>", unsafe_allow_html=True)
    
    if st.session_state.usuario is None:
        aba_ac = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        with aba_ac[0]:
            ln, ls = st.text_input("Nome:").strip().title(), st.text_input("Senha:", type="password")
            if st.button("Acessar"):
                du = carregar_dados("Usuarios")
                if not du[(du['nome']==ln) & (du['senha'].astype(str)==ls)].empty:
                    st.session_state.usuario = ln
                    st.rerun()
                else: st.error("Erro!")
        with aba_ac[1]:
            with st.form("f_c"):
                n, tel, m, d, s = st.text_input("Nome:"), st.text_input("WhatsApp:"), st.selectbox("Ministério:", ["Louvor", "Irmãs", "Jovens", "Varões", "Mídia", "Visitante"]), st.date_input("Nascimento:", min_value=datetime(1950,1,1)), st.text_input("Senha:", type="password")
                if st.form_submit_button("Ok") and n and s:
                    if salvar_novo_usuario([n, tel, m, str(d), s, 1, "Plano Anual"]): st.success("Ok!")
    else:
        u, df_l, df_p = st.session_state.usuario, carregar_dados("Leitura"), carregar_dados("Progresso")
        if not df_l.empty:
            p_sel = st.selectbox("Plano:", df_l['plano'].unique())
            dia_p = 1
            if not df_p.empty:
                df_p.columns = [str(c).lower().strip() for c in df_p.columns]
                prog = df_p[(df_p['usuario']==u) & (df_p['plano']==p_sel)]
                if not prog.empty: dia_p = int(prog.iloc[0]['dia_atual'])
            
            l_hj = df_l[(df_l['plano']==p_sel) & (pd.to_numeric(df_l['dia'])==dia_p)]
            
            if not l_hj.empty:
                l = l_hj.iloc[0]
                ref = l.get('referencia', '---')
                st.markdown(f"### 📍 Dia {dia_p}")
                
                # Layout da Referência
                st.markdown(f'<div style="background:rgba(10,61,98,0.4); padding:20px; border-radius:15px; border-left:5px solid #00b894; margin-bottom:20px;">{ref}</div>', unsafe_allow_html=True)
                
                with st.spinner('Buscando versículos...'):
                    txts = buscar_capitulos_divididos(ref)
                
                if "Erro" not in txts:
                    abs_b = st.tabs(list(txts.keys()))
                    for i, ab_c in enumerate(abs_b):
                        with ab_c:
                            # CORREÇÃO: white-space: pre-wrap para quebrar as linhas
                            st.markdown(f"""
                                <div style="
                                    text-align: justify; 
                                    line-height: 1.8; 
                                    white-space: pre-wrap; 
                                    background: rgba(255,255,255,0.03); 
                                    padding: 15px; 
                                    border-radius: 10px;
                                    font-size: 1.1em;
                                    color: white;
                                ">
                                    {txts[list(txts.keys())[i]]}
                                </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"💡 Meditação: {l.get('resumo_para_meditacao', '---')}")
                
                if st.button("✅ Concluir Leitura de Hoje", use_container_width=True):
                    if atualizar_progresso_planilha(u, p_sel, dia_p + 1):
                        st.balloons()
                        st.rerun()
            else:
                st.success("🎉 Parabéns! Plano Concluído!")
                if st.button("Reiniciar Plano"): 
                    atualizar_progresso_planilha(u, p_sel, 1)
                    st.rerun()
        
        st.divider()
        if st.button("Sair da Conta"): 
            st.session_state.usuario = None
            st.rerun()
            # Redes Sociais Fixas no Rodapé de todas as páginas
st.markdown(f"""
    <div class="footer-social">
        <a href="https://www.instagram.com/isosedcosmopolissp/" target="_blank">📸 Instagram</a>
        <a href="https://www.facebook.com/isosedcosmopolissp/" target="_blank">🔵 Facebook</a>
    </div>
    <br><br><br> """, unsafe_allow_html=True)
