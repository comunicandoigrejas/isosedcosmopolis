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

# --- CSS: CAIXAS BRANCAS COM FONTE PRETA / BOTÕES AZUIS ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    p, span, div, label, .stMarkdown { color: white !important; }
    h1, h2, h3, b, strong { color: #ffd700 !important; text-align: center; }

    /* CAIXAS DE ENTRADA: FUNDO BRANCO E FONTE PRETA */
    input, textarea, [data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ffd700 !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] { color: black !important; font-weight: bold; }
    
    /* BOTÕES AZUIS */
    div.stButton > button, div.stFormSubmitButton > button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border: 2px solid #ffd700 !important;
        border-radius: 10px !important; font-weight: bold !important; height: 3.5em !important;
    }
    .card-isosed { background: rgba(255, 215, 0, 0.05) !important; border: 1px solid #ffd700 !important; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONEXÃO E APOIO ---
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
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]] # Qua, Sex, Dom
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

# =========================================================
# --- ROTEADOR ---
# =========================================================

# --- 1. INÍCIO ---
if st.session_state.pagina == "Início":
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    # Santa Ceia
    df_ag = carregar_dados("Agenda")
    prox = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em; color:#ffd700;">{prox} às 18h00</b></div>', unsafe_allow_html=True)

    # Menu
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

# --- PÁGINA: AGENDA ---
elif st.session_state.pagina == "Agenda":
    # Botão de Voltar centralizado e grande para o polegar
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_agenda")
    
    st.markdown("<h2>🗓️ Agenda ISOSED 2026</h2>", unsafe_allow_html=True)
    
    # Carrega os dados da aba "Agenda"
    df_agenda = carregar_dados("Agenda")
    
    # Cria as 12 abas dos meses
    nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    abas = st.tabs(nomes_meses)
    
    if not df_agenda.empty:
        # 1. Garante que a coluna 'data' seja tratada como data real
        df_agenda['data_dt'] = pd.to_datetime(df_agenda['data'], dayfirst=True, errors='coerce')
        
        # 2. Loop para preencher cada aba de mês
        for i, aba in enumerate(abas):
            with aba:
                # Filtra os eventos pelo número do mês (i+1)
                mes_atual = i + 1
                eventos_mes = df_agenda[df_agenda['data_dt'].dt.month == mes_atual].sort_values('data_dt')
                
                if not eventos_mes.empty:
                    for _, linha in eventos_mes.iterrows():
                        # Exibe cada evento em um card compacto
                        st.markdown(f"""
                            <div class="card-isosed">
                                <b style="color:#ffd700; font-size:1.1em;">{linha['data']}</b><br>
                                <span style="color:white;">{linha['evento']}</span>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Nenhum evento cadastrado para {calendar.month_name[mes_atual]}.")
    else:
        st.warning("⚠️ Nenhuma informação encontrada na aba 'Agenda' da planilha.")

# --- PÁGINA: ANIVERSÁRIOS ---
elif st.session_state.pagina == "Aniv":
    # Botão de Voltar
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_aniv")
    
    st.markdown("<h2>🎂 Quadro de Aniversariantes</h2>", unsafe_allow_html=True)
    
    # Carrega os dados da aba "Aniversariantes"
    df_aniv = carregar_dados("Aniversariantes")
    
    # Cria as 12 abas dos meses
    meses_lista = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    abas_mes = st.tabs(meses_lista)
    
    if not df_aniv.empty:
        # Identifica a coluna de mês (trata 'mes' ou 'mês')
        col_mes = next((c for c in df_aniv.columns if 'mes' in c or 'mês' in c), None)
        col_dia = next((c for c in df_aniv.columns if 'dia' in c), None)
        col_nome = next((c for c in df_aniv.columns if 'nome' in c), None)

        if col_mes and col_dia and col_nome:
            for i, aba in enumerate(abas_mes):
                with aba:
                    num_mes = i + 1
                    # Filtra e ordena por dia
                    lista_mes = df_aniv[df_aniv[col_mes].astype(int) == num_mes].sort_values(col_dia)
                    
                    if not lista_mes.empty:
                        for _, r in lista_mes.iterrows():
                            st.markdown(f"""
                                <div class="card-aniv">
                                    <span style="font-size:1.1em;">🎁 Dia {r[col_dia]} - {r[col_nome]}</span>
                                end
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Nenhum aniversariante registado para este mês.")
        else:
            st.error("⚠️ Verifique se as colunas 'nome', 'dia' e 'mes' existem na planilha.")
    else:
        st.warning("⚠️ Aba 'Aniversariantes' está vazia ou não foi encontrada.")

# --- PÁGINA: GESTÃO ---
elif st.session_state.pagina == "Gestao":
    # CSS Específico para esta página: Caixas Brancas com Fonte Preta
    st.markdown("""
        <style>
        /* Força fundo branco e fonte preta em todos os campos de entrada */
        input, textarea, [data-baseweb="select"] > div {
            background-color: white !important;
            color: black !important;
            border: 2px solid #ffd700 !important;
        }
        /* Garante que o texto digitado seja preto */
        .stTextInput input {
            color: black !important;
            -webkit-text-fill-color: black !important;
        }
        /* Ajusta a cor da fonte dentro do seletor (selectbox) */
        div[data-baseweb="select"] {
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_gestao")
    
    st.markdown("<h2>⚙️ Painel de Administração</h2>", unsafe_allow_html=True)

    # 1. Sistema de Login Admin
    if not st.session_state.admin_ok:
        with st.form("login_admin"):
            st.markdown("<p style='text-align:center;'>Digite a senha master para liberar as ferramentas:</p>", unsafe_allow_html=True)
            senha_gestao = st.text_input("Senha:", type="password")
            
            if st.form_submit_button("LIBERAR ACESSO"):
                if senha_gestao == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")
    
    # 2. Painel de Ferramentas (Só aparece após o login)
    else:
        st.success("Acesso Liberado! Bem-vindo, Administrador.")
        
        tab_estatistica, tab_gerador = st.tabs(["📊 Estatísticas", "🤖 Gerar Escalas"])
        
        with tab_estatistica:
            df_usuarios = carregar_dados("Usuarios")
            st.metric("Total de Membros Cadastrados", len(df_usuarios))
            if not df_usuarios.empty:
                st.dataframe(df_usuarios, use_container_width=True)

        with tab_gerador:
            st.write("Crie o rodízio do próximo mês automaticamente:")
            
            # Formulário de Geração
            with st.form("gerador_escalas"):
                c1, c2 = st.columns(2)
                mes_gen = c1.selectbox("Mês:", list(range(1, 13)), index=hoje_br.month - 1)
                ano_gen = c2.number_input("Ano:", value=2026)
                
                setor_gen = st.radio("Selecione o Setor:", ["Fotografia", "Recepção", "Som/Mídia"])
                
                if st.form_submit_button(f"GERAR ESCALA DE {setor_gen.upper()}"):
                    # Aqui entra a lógica de salvar na planilha que vimos anteriormente
                    st.info(f"Processando geração para {setor_gen} em {mes_gen}/{ano_gen}...")
                    # (A função de salvar seria chamada aqui)

# --- 3. LEITURA (CADASTRO COM ESCOLHA DE PLANO) ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    if st.session_state.user is None:
        t1, t2 = st.tabs(["Login", "Novo Cadastro"])
        with t1:
            with st.form("l_f"):
                tel = st.text_input("WhatsApp:"); sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Entrar"):
                    df_u = carregar_dados("Usuarios")
                    u_f = df_u[(df_u['telefone'].astype(str) == str(tel)) & (df_u['senha'].astype(str) == str(sen))]
                    if not u_f.empty: st.session_state.user = u_f.iloc[0].to_dict(); st.rerun()
        with t2:
            with st.form("c_f"):
                st.write("Escolha seu plano para começar:")
                plano_opt = st.selectbox("Plano de Leitura:", ["Anual 2026", "Novo Testamento", "Casais", "Infantil"])
                n = st.text_input("Nome:"); t = st.text_input("WhatsApp:"); s = st.text_input("Senha:", type="password")
                if st.form_submit_button("Criar Conta e Começar"):
                    sh = conectar_planilha()
                    sh.worksheet("Usuarios").append_row([n, t, "Membro", "", s, 1, plano_opt])
                    sh.worksheet("Progresso").append_row([t, plano_opt, 1])
                    st.success("Conta criada! Vá em Login.")
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        p_row = df_p[df_p['usuario'].astype(str) == str(u['telefone'])]
        if not p_row.empty:
            dia = int(p_row.iloc[0]['dia_atual'])
            st.markdown(f"### Olá, {u['nome']}! Dia {dia}")
            # Aqui ele puxa o conteúdo da aba Leitura filtrando por Dia e Plano
            st.info(f"Você está seguindo o plano: {u['plano_escolhido']}")
            if st.button("✅ Marcar como Lido"):
                sh = conectar_planilha(); cell = sh.worksheet("Progresso").find(str(u['telefone']))
                sh.worksheet("Progresso").update_cell(cell.row, 3, dia + 1); st.rerun()

# --- 4. ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    df = carregar_dados("Escalas")
    t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som/Mídia", "🤝 Recepção"])
    if not df.empty:
        df['dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        prox = df[df['dt'].dt.date >= hoje_br].sort_values('dt')
        for t, dep in zip([t1, t2, t3], ["Foto", "Mídia", "Recepção"]):
            with t:
                f = prox[prox['departamento'].str.contains(dep, case=False, na=False)]
                for _, r in f.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)

# --- PÁGINA: DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    # Botão de Voltar
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_dev")
    
    st.markdown("<h2>📖 Devocional Diário</h2>", unsafe_allow_html=True)
    
    # Carrega os dados da aba "Devocional"
    df_dev = carregar_dados("Devocional")
    
    if not df_dev.empty:
        # Puxa sempre a última linha cadastrada (o devocional mais recente)
        item = df_dev.iloc[-1]
        
        # Exibição do Título e Tema
        st.markdown(f"""
            <div class="card-isosed" style="text-align:center;">
                <h3 style="margin:0; color:#ffd700;">{item['titulo']}</h3>
                <p style="margin:5px 0 0 0; opacity:0.8; font-size:0.9em;">
                    ✨ Tema: {item['tema']} | 📅 {item['data']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Versículo em destaque
        st.success(f"📖 **Versículo Chave:** {item['versiculo']}")
        
        # Texto Principal
        st.markdown("#### Palavra de Hoje")
        st.write(item['texto'])
        
        st.markdown("---")
        
        # Aplicação e Desafio em menus expansíveis (melhor para Mobile)
        with st.expander("🎯 APLICAÇÃO PESSOAL"):
            st.write(item['aplicacao'])
            
        with st.expander("🔥 DESAFIO DO DIA"):
            st.write(item['desafio'])
            
    else:
        st.warning("⚠️ Nenhum devocional encontrado na aba 'Devocional' da planilha.")
