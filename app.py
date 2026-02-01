import streamlit as st
from openai import OpenAI
import urllib.parse
import pandas as pd
import time

# ==========================================
# 📊 ÁREA DE DADOS (FORNEÇA AS INFORMAÇÕES AQUI)
# ==========================================

# 1. LISTA DE USUÁRIOS (Email, Senha, Status, Perfil, ID da Igreja)
def carregar_usuarios_local():
    dados = [
        {"email": "admin@teste.com", "senha": "123", "status": "ativo", "perfil": "admin", "igreja_id": "001"},
        {"email": "igreja@teste.com", "senha": "456", "status": "ativo", "perfil": "usuario", "igreja_id": "002"},
        # Adicione mais usuários aqui seguindo o mesmo padrão
    ]
    return pd.DataFrame(dados)

# 2. CONFIGURAÇÕES DAS IGREJAS (ID, Nome, Cor, Instagram, Hashtags, DNA)
def carregar_configuracoes_local():
    dados = [
        {
            "igreja_id": "001",
            "nome_exibicao": "Igreja Sede Principal",
            "cor_tema": "#1E90FF",
            "instagram_url": "https://instagram.com/igreja_exemplo",
            "hashtags_fixas": "#fé #igreja #comunidade",
            "dna_ministerial": "Igreja tradicional com foco em ensino teológico profundo."
        },
        {
            "igreja_id": "002",
            "nome_exibicao": "Comunidade Jovem",
            "cor_tema": "#FF4500",
            "instagram_url": "https://instagram.com/jovens_exemplo",
            "hashtags_fixas": "#jovens #adoração #cristo",
            "dna_ministerial": "Ministério dinâmico focado em jovens e música contemporânea."
        },
    ]
    return pd.DataFrame(dados)

# ==========================================
# ⚙️ CONFIGURAÇÕES DO SISTEMA
# ==========================================

st.set_page_config(
    page_title="Comunicando Igrejas Pro", 
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicialização de Estado
if "logado" not in st.session_state: st.session_state.logado = False
if "cor_previa" not in st.session_state: st.session_state.cor_previa = None
if "email_salvo" not in st.session_state: st.session_state.email_salvo = ""
if "df_conf" not in st.session_state: st.session_state.df_conf = carregar_configuracoes_local()

for chave in ["perfil", "igreja_id", "email"]:
    if chave not in st.session_state: st.session_state[chave] = ""

# CSS Responsivo e Visual (MANTIDO)
st.markdown("""
    <style>
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
    footer { visibility: hidden !important; }
    .block-container { padding-top: 1rem !important; max-width: 85% !important; margin: auto; }
    .church-title { text-align: center; font-size: 2.2rem; font-weight: 800; margin-bottom: 1.5rem; text-transform: uppercase; }
    @media (max-width: 768px) {
        .block-container { max-width: 100% !important; padding: 0.5rem !important; }
        .church-title { font-size: 1.4rem !important; }
        .stTabs [data-baseweb="tab"] { padding: 5px !important; font-size: 0.8rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# Conexão OpenAI (MANTIDA)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    ASSISTANT_ID = st.secrets["OPENAI_ASSISTANT_ID"]
except Exception:
    st.error("Erro nos Secrets da OpenAI.")
    st.stop()

def chamar_super_agente(comando):
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(thread_id=thread.id, role="user", content=comando)
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)
    while run.status != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    mensagens = client.beta.threads.messages.list(thread_id=thread.id)
    return mensagens.data[0].content[0].text.value

# ==========================================
# 🚪 INTERFACE DE LOGIN
# ==========================================
if not st.session_state.logado:
    st.markdown("<h1 style='text-align: center;'>🚀 Comunicando Igrejas</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.form("login"):
            em = st.text_input("E-mail", value=st.session_state.email_salvo)
            se = st.text_input("Senha", type="password")
            lembrar = st.checkbox("Lembrar e-mail", value=True if st.session_state.email_salvo else False)
            if st.form_submit_button("Entrar no Painel", use_container_width=True):
                df_u = carregar_usuarios_local()
                u = df_u[(df_u['email'].str.lower() == em.lower()) & (df_u['senha'].astype(str) == str(se))]
                if not u.empty and str(u.iloc[0]['status']).strip().lower() == 'ativo':
                    st.session_state.logado, st.session_state.perfil, st.session_state.igreja_id, st.session_state.email = True, str(u.iloc[0]['perfil']).strip().lower(), u.iloc[0]['igreja_id'], em
                    st.session_state.email_salvo = em if lembrar else ""
                    st.rerun()
                else: st.error("Acesso negado.")

# ==========================================
# ⛪ AMBIENTE LOGADO
# ==========================================
else:
    df_conf = st.session_state.df_conf
    if st.session_state.perfil == "admin":
        escolha = st.selectbox("💎 Gestor Master", df_conf['nome_exibicao'].tolist())
        conf = df_conf[df_conf['nome_exibicao'] == escolha].iloc[0]
    else:
        conf = df_conf[df_conf['igreja_id'] == st.session_state.igreja_id].iloc[0]

    cor_atual = st.session_state.cor_previa if st.session_state.cor_previa else str(conf['cor_tema'])
    dna_salvo = str(conf['dna_ministerial'])

    st.markdown(f"<style>.stButton>button {{ background-color: {cor_atual} !important; color: white !important; }} .stTabs [aria-selected='true'] {{ background-color: {cor_atual} !important; color: white !important; }} .church-title {{ color: {cor_atual}; }}</style><div class='church-title'>{conf['nome_exibicao']}</div>", unsafe_allow_html=True)

    t_gen, t_story, t_brief, t_insta, t_perf, t_sair = st.tabs(["✨ Leg.", "🎬 Sto.", "🎨 Brief.", "📸 Insta", "⚙️ Perf.", "🚪 Sair"])

    with t_gen:
        st.header("✨ Legendas ARA")
        rede = st.selectbox("Rede", ["Instagram", "Facebook"])
        tom = st.selectbox("Tom", ["Inspirador", "Pentecostal", "Jovem", "Teológico"])
        ver, ht = st.text_input("📖 Versículo ARA"), st.text_input("🏷️ Hashtags")
        tema = st.text_area("📝 Tema do post")
        if st.button("🚀 Gerar Legenda", use_container_width=True):
            res = chamar_super_agente(f"DNA: {dna_salvo}. Legenda {rede}, tom {tom}, tema {tema}, versículo {ver}. ARA. Hashtags: {conf['hashtags_fixas']} {ht}")
            st.info(res)
            st.link_button("📲 Enviar WhatsApp", f"https://api.whatsapp.com/send?text={urllib.parse.quote(res)}", use_container_width=True)

    with t_story:
        st.header("🎬 Roteiro Stories")
        ts = st.text_input("Tema da sequência:")
        if st.button("🎬 Criar Roteiro", use_container_width=True):
            st.success(chamar_super_agente(f"DNA: {dna_salvo}. 3 stories sobre {ts} para {conf['nome_exibicao']}."))

    with t_brief:
        st.header("🎨 Briefing Visual")
        tema_b = st.text_input("🎯 Tema")
        formato_b = st.selectbox("🖼️ Formato", ["Único", "Carrossel", "Reels", "Cartaz"])
        if st.button("🎨 Gerar Briefing", use_container_width=True):
            res_b = chamar_super_agente(f"Diretor de Arte. DNA: {dna_salvo}. Briefing tema: '{tema_b}' formato {formato_b}.")
            st.warning(res_b)
            texto_wa = f"*🎨 BRIEFING - {conf['nome_exibicao']}*\n*🎯 TEMA:* {tema_b}\n*📋:* {res_b}"
            st.link_button("📲 Enviar ao Designer", f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_wa)}", use_container_width=True)

    with t_insta:
        st.header("📸 Instagram")
        st.link_button("Ir para o Perfil", str(conf['instagram_url']), use_container_width=True)
        st.link_button("✨ Criar Nova Postagem", "https://www.instagram.com/create/select/", use_container_width=True)

    with t_perf:
        st.header("⚙️ Perfil")
        dna_input = st.text_area("Atualizar DNA:", value="", placeholder="Digite para atualizar...")
        st.caption(f"**DNA atual:** {dna_salvo[:100]}...")
        nova_cor = st.color_picker("Cor do sistema:", cor_atual)
        if st.button("💾 Salvar Temporariamente", use_container_width=True):
            # Atualiza apenas na memória da sessão atual
            st.session_state.cor_previa = nova_cor
            # Localiza e atualiza o DNA no DataFrame da sessão
            idx = st.session_state.df_conf.index[st.session_state.df_conf['igreja_id'] == conf['igreja_id']].tolist()
            if idx and dna_input.strip():
                st.session_state.df_conf.at[idx[0], 'dna_ministerial'] = dna_input
            st.success("✅ Atualizado para esta sessão!")
            time.sleep(1)
            st.rerun()

    with t_sair:
        if st.button("🔴 Confirmar Logout", use_container_width=True):
            em_temp = st.session_state.email_salvo
            st.session_state.clear()
            st.session_state.email_salvo = em_temp
            st.rerun()
