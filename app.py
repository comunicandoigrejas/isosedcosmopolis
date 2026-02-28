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
    # DICIONÁRIO DE MESES EM PORTUGUÊS
    meses_pt = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    # LISTA DE ANOS (Para evitar erros de digitação)
    anos_disponiveis = [2026, 2027, 2028]

    st.markdown("""
        <style>
        /* FORÇA O TEXTO DE DENTRO DAS CAIXAS A FICAR PRETO */
        div[data-baseweb="select"] * {
            color: black !important;
            -webkit-text-fill-color: black !important;
        }

        /* GARANTE O FUNDO BRANCO NAS CAIXAS */
        div[data-baseweb="select"] > div, input {
            background-color: white !important;
        }

        /* LISTA DE OPÇÕES (DROPDOWN) */
        div[data-baseweb="popover"] * {
            color: black !important;
            background-color: white !important;
        }

        /* DESTAQUE AO SELECIONAR */
        div[data-baseweb="popover"] li:hover {
            background-color: #ffd700 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_gestao")
    
    st.markdown("<h2>⚙️ Gestão de Escalas</h2>", unsafe_allow_html=True)

    if not st.session_state.admin_ok:
        with st.form("login_admin"):
            senha_gestao = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("LIBERAR ACESSO"):
                if senha_gestao == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
    else:
        st.success("Painel Administrativo Ativo")
        
        with st.form("gerador_escalas_ano"):
            st.write("### 🤖 Configurar Novo Rodízio")
            
            # MÊS E ANO LADO A LADO
            col_mes, col_ano = st.columns(2)
            
            with col_mes:
                mes_selecionado = st.selectbox(
                    "Mês:", 
                    options=list(meses_pt.keys()), 
                    format_func=lambda x: meses_pt[x],
                    index=hoje_br.month - 1
                )
            
            with col_ano:
                ano_selecionado = st.selectbox(
                    "Ano:", 
                    options=anos_disponiveis,
                    index=0 # Começa em 2026
                )
            
            setor_selecionado = st.radio("Setor da Igreja:", ["Fotografia", "Recepção", "Som/Mídia"])
            
            if st.form_submit_button(f"GERAR ESCALA DE {setor_selecionado.upper()}"):
                # Aqui o App usará o mes_selecionado e o ano_selecionado para calcular as datas
                st.info(f"Gerando {setor_selecionado} para {meses_pt[mes_selecionado]} de {ano_selecionado}...")
                # Lógica de salvar na planilha...)
    
# --- PÁGINA: LEITURA ---
elif st.session_state.pagina == "Leitura":
    # CSS para garantir Caixas Brancas e Fonte Preta no Login/Cadastro
    st.markdown("""
        <style>
        input, [data-baseweb="select"] > div { background-color: white !important; color: black !important; }
        .stTextInput input { color: black !important; }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_leitura")
    
    # 1. TELA DE ACESSO (Se não estiver logado)
    if st.session_state.user is None:
        tab_login, tab_cadastro = st.tabs(["🔐 Entrar", "📝 Novo Cadastro"])
        
        with tab_login:
            with st.form("form_login_nome"):
                st.markdown("<p style='color:white;'>Acesse seu plano de leitura:</p>", unsafe_allow_html=True)
                login_nome = st.text_input("Digite seu Nome:")
                login_senha = st.text_input("Senha:", type="password")
                
                if st.form_submit_button("ENTRAR NO PLANO"):
                    df_usuarios = carregar_dados("Usuarios")
                    # Busca pelo Nome e Senha
                    user_match = df_usuarios[
                        (df_usuarios['nome'].astype(str).str.lower() == login_nome.lower()) & 
                        (df_usuarios['senha'].astype(str) == login_senha)
                    ]
                    
                    if not user_match.empty:
                        st.session_state.user = user_match.iloc[0].to_dict()
                        st.success(f"Bem-vindo, {login_nome}!")
                        st.rerun()
                    else:
                        st.error("Nome ou senha não encontrados. Verifique a grafia.")

        with tab_cadastro:
            with st.form("form_cadastro_completo"):
                st.write("Crie sua conta bíblica:")
                novo_nome = st.text_input("Nome Completo:")
                novo_zap = st.text_input("WhatsApp (com DDD):")
                nova_senha = st.text_input("Crie uma Senha:", type="password")
                plano_escolhido = st.selectbox("Escolha seu Plano:", ["Anual 2026", "Novo Testamento", "Casais"])
                
                if st.form_submit_button("CADASTRAR E COMEÇAR"):
                    if novo_nome and novo_zap and nova_senha:
                        sh = conectar_planilha()
                        # Grava na aba Usuarios (Mantendo o Zap no registro)
                        sh.worksheet("Usuarios").append_row([novo_nome, novo_zap, "Membro", "", nova_senha, 1, plano_escolhido])
                        # Inicia o histórico na aba Progresso
                        sh.worksheet("Progresso").append_row([novo_zap, plano_escolhido, 1])
                        st.success("Conta criada com sucesso! Agora é só fazer o Login.")
                    else:
                        st.warning("Preencha todos os campos.")

    # 2. TELA DE PROGRESSO (Se já estiver logado)
    else:
        u = st.session_state.user
        st.markdown(f"### 📖 Plano de Leitura: {u['nome']}")
        
        # Puxa o progresso real da aba 'Progresso' usando o WhatsApp (zap) do usuário logado
        df_progresso = carregar_dados("Progresso")
        # Coluna 'usuario' na planilha deve conter o WhatsApp
        minha_linha = df_progresso[df_progresso['usuario'].astype(str) == str(u['telefone'])]
        
        if not minha_linha.empty:
            dia_atual = int(minha_linha.iloc[0]['dia_atual'])
            plano_ativo = minha_linha.iloc[0]['plano']
            
            st.markdown(f"""
                <div class="card-isosed">
                    <span style="font-size:1.2em;">📍 Você está no <b>Dia {dia_atual}</b></span><br>
                    <span style="opacity:0.8;">Plano: {plano_ativo}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # Puxa a leitura do dia da aba 'Leitura'
            df_leituras = carregar_dados("Leitura")
            leitura_hoje = df_leituras[
                (df_leituras['dia'].astype(str) == str(dia_atual)) & 
                (df_leituras['plano'].astype(str).str.lower() == plano_ativo.lower())
            ]
            
            if not leitura_hoje.empty:
                l = leitura_hoje.iloc[0]
                st.info(f"📖 **HOJE:** {l['referencia']}")
                st.write(f"💡 *Meditação:* {l['resumo']}")
                
                if st.button("✅ CONCLUIR LEITURA DE HOJE"):
                    sh = conectar_planilha()
                    aba_p = sh.worksheet("Progresso")
                    # Localiza a célula certa para atualizar o dia
                    cell = aba_p.find(str(u['telefone']))
                    aba_p.update_cell(cell.row, 3, dia_atual + 1)
                    st.balloons()
                    st.success("Parabéns! Progresso salvo.")
                    st.rerun()
            else:
                st.warning("Leitura não configurada para este dia/plano na planilha.")
        
        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()

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
        # Puxa o último devocional cadastrado
        item = df_dev.iloc[-1]
        
        # 1. Título e Tema (Fixo no topo)
        st.markdown(f"""
            <div style="text-align:center; margin-bottom: 20px;">
                <h3 style="color:#ffd700; margin-bottom:0;">{item['titulo']}</h3>
                <p style="color:white; opacity:0.8; font-size:0.9em;">✨ Tema: {item['tema']} | 📅 {item['data']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 2. Versículo (Em destaque Amarelo/Dourado)
        st.warning(f"📖 **VERSÍCULO CHAVE:** {item['versiculo']}")
        
        # 3. Texto da Palavra
        st.markdown("#### 📜 Mensagem de Hoje")
        st.write(item['texto'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 4. APLICAÇÃO PESSOAL (Texto Fixo em bloco Azul)
        st.info(f"🎯 **APLICAÇÃO PESSOAL:** \n\n {item['aplicacao']}")
        
        # 5. DESAFIO DO DIA (Texto Fixo em bloco Verde)
        st.success(f"🔥 **DESAFIO DO DIA:** \n\n {item['desafio']}")
        
        st.markdown("<br><p style='text-align:center; opacity:0.5; font-size:0.8em;'>ISOSED Cosmópolis - 2026</p>", unsafe_allow_html=True)
            
    else:
        st.error("⚠️ Nenhum devocional encontrado. Verifique a planilha 'Devocional'.")
