import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO E MEMÓRIA (No Topo) ---
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

# --- 2. FUNÇÕES DE BANCO DE DADOS (Organizadas para não quebrar o código) ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normalização dos cabeçalhos: minúsculo, sem acento e troca ESPAÇO por UNDERSCORE (_)
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c').replace(' ', '_') for c in df.columns]
            
            # LIMPEZA DE DADOS: Remove espaços em branco de todas as células de texto
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
    except Exception as e:
        st.error(f"Erro ao gravar na planilha: {e}")
        return False

def atualizar_progresso_planilha(usuario, plano, novo_dia):
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Progresso")
        # Lê os dados existentes para encontrar a linha certa
        dados = aba.get_all_records()
        df_p = pd.DataFrame(dados)
        
        if not df_p.empty:
            # Normaliza nomes para busca
            df_p.columns = [str(c).lower().strip() for c in df_p.columns]
            linha = df_p[(df_p['usuario'] == usuario) & (df_p['plano'] == plano)]
            
            if not linha.empty:
                # Atualiza a linha existente (Coluna 3 é 'dia_atual')
                idx = linha.index[0] + 2 
                aba.update_cell(idx, 3, int(novo_dia))
                return True
        
        # Se não existir, cria uma linha nova
        aba.append_row([usuario, plano, int(novo_dia)])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar progresso: {e}")
        return False

# --- 3. SEU ESTILO CSS ORIGINAL ---
st.markdown("""
    <style>
  /* --- BARRA DE MESES HORIZONTAL (Scroll Mobile) --- */
    @media (max-width: 768px) {
        /* Alvo: O bloco que contém os botões de meses */
        div[data-testid="stHorizontalBlock"]:has(button[key*="mes_"]),
        div[data-testid="stHorizontalBlock"]:has(button[key*="an_"]),
        div[data-testid="stHorizontalBlock"]:has(button[key*="aniv_"]) {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important; /* Impede de empilhar */
            overflow-x: auto !important; /* Ativa o scroll lateral */
            overflow-y: hidden !important;
            width: 100% !important;
            padding: 10px 0px !important;
            gap: 8px !important;
        }

        /* Alvo: As colunas individuais dentro desse bloco */
        div[data-testid="stHorizontalBlock"]:has(button[key*="mes_"]) > div,
        div[data-testid="stHorizontalBlock"]:has(button[key*="an_"]) > div,
        div[data-testid="stHorizontalBlock"]:has(button[key*="aniv_"]) > div {
            width: 80px !important; /* Define uma largura fixa para cada mês */
            min-width: 80px !important;
            max-width: 80px !important;
            flex: 0 0 80px !important; /* Não deixa a coluna crescer nem diminuir */
        }

        /* Estilo do botão para caber no scroll */
        div[data-testid="stHorizontalBlock"] button[data-testid="stBaseButton-secondary"] {
            width: 80px !important;
            height: 40px !important;
            font-size: 11px !important;
        }
    }
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { color: #FFFFFF !important; font-weight: 800 !important; }
    button[data-testid="stBaseButton-secondary"] {
        width: 150px !important; height: 65px !important;
        background-color: #0a3d62 !important; border-radius: 12px !important;
        border: 2px solid #3c6382 !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }
    button[data-testid="stBaseButton-secondary"] p { color: #FFFFFF !important; font-weight: 900 !important; text-transform: uppercase !important; }
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

# --- 4. ROTEADOR DE PÁGINAS (Mantendo seus Layouts Intocados) ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
        segunda_proxima = domingo_atual + timedelta(days=8)
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.button("🗓️ Agenda", key="bt_1", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", key="bt_2", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", key="bt_3", on_click=navegar, args=("AnivMês",))
    with c2:
        st.button("📢 Escalas", key="bt_4", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", key="bt_5", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", key="bt_6", on_click=navegar, args=("Leitura",))
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=200)

elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_ag")
    st.markdown("<h1>🗓️ Agenda ISOSED 2026</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        meses_lista = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
        cols_meses = st.columns(12)
        mes_sel = st.session_state.get('mes_agenda', hoje_br.month)
        for i, (num, nome) in enumerate(meses_lista.items()):
            if cols_meses[i].button(nome, key=f"mes_{num}"):
                st.session_state.mes_agenda = num
                st.rerun()
        
        eventos_mes = df[df['data'].dt.month == st.session_state.get('mes_agenda', hoje_br.month)].sort_values(by='data')
        for _, r in eventos_mes.iterrows():
            dia_f = r['data'].strftime('%d/%m')
            st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0a3d62;"><span style="color: #ffd700; font-weight: bold;">{dia_f}</span> - <span style="color: white;">{r["evento"]}</span></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_gr")
    st.markdown("<h1>👥 Grupos e Departamentos</h1>", unsafe_allow_html=True)
    df = carregar_dados("Agenda")
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        deptos = ["Jovens", "Varões", "Irmãs", "Louvor", "Missões", "Tarde com Deus"]
        tabs = st.tabs(deptos)
        for i, depto in enumerate(deptos):
            with tabs[i]:
                filtro = df[df['evento'].str.contains(depto, case=False, na=False)].sort_values(by='data')
                if not filtro.empty:
                    for _, r in filtro.iterrows():
                        dia = r['data'].strftime('%d/%m/%Y')
                        st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; margin-bottom: 8px; border-left: 5px solid #00b894;"><b style="color: #00b894;">{dia}</b> — <span style="color: white;">{r["evento"]}</span></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_an")
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        df['mes'] = pd.to_numeric(df['mes'], errors='coerce')
        df['dia'] = pd.to_numeric(df['dia'], errors='coerce')
        meses_lista = {1:"Jan", 2:"Fev", 3:"Mar", 4:"Abr", 5:"Mai", 6:"Jun", 7:"Jul", 8:"Ago", 9:"Set", 10:"Out", 11:"Nov", 12:"Dez"}
        cols = st.columns(12)
        if 'mes_an' not in st.session_state: st.session_state.mes_an = hoje_br.month
        for i, (num, nome) in enumerate(meses_lista.items()):
            if cols[i].button(nome, key=f"an_{num}"):
                st.session_state.mes_an = num
                st.rerun()
        lista = df[df['mes'] == st.session_state.mes_an].sort_values(by='dia')
        for _, r in lista.iterrows():
            st.markdown(f'<div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #f1c40f;"><span style="color: #f1c40f; font-weight: bold;">Dia {int(r["dia"]):02d}</span> - <span style="color: white; font-size: 1.1em;">{r["nome"]}</span></div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_es")
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df = carregar_dados("Midia")
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📅 {r.get('data','')} - {r.get('culto','')}"):
                    st.write(f"**Operador:** {r.get('op','')} | **Foto:** {r.get('foto','')} | **Chegada:** {r.get('chegada','')}")
    with t2:
        df = carregar_dados("Recepcao")
        if not df.empty:
            for _, r in df.iterrows():
                with st.expander(f"📅 {r.get('data','')} ({r.get('dia','')})"):
                    st.write(f"**Dupla:** {r.get('dupla','')} | **Chegada:** {r.get('chegada','')}")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_me")
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        dt_str = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == dt_str]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"**Tema:** {d.get('tema', '')}")
            st.markdown(f"### {d.get('titulo', '')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', ''))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', ''))

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="vol_le")
    st.markdown("<h1>📜 Área do Leitor</h1>", unsafe_allow_html=True)
    
    if st.session_state.usuario is None:
        aba_ac = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        with aba_ac[0]:
            l_nome = st.text_input("Nome completo:", key="l_n").strip().title()
            l_senha = st.text_input("Senha:", type="password", key="l_s")
            if st.button("Acessar", key="l_b"):
                df_u = carregar_dados("Usuarios")
                if not df_u.empty:
                    match = df_u[(df_u['nome'] == l_nome) & (df_u['senha'].astype(str) == str(l_senha))]
                    if not match.empty:
                        st.session_state.usuario = l_nome
                        st.rerun()
                    else: st.error("Nome ou senha incorretos.")
        with aba_ac[1]:
            with st.form("f_cad"):
                n = st.text_input("Nome Completo:").strip().title()
                tel = st.text_input("WhatsApp:")
                minis = st.selectbox("Ministério:", ["Louvor", "Irmãs", "Jovens", "Varões", "Mídia", "Crianças", "Visitante"])
                nasc = st.date_input("Nascimento:", min_value=datetime(1950, 1, 1), max_value=hoje_br)
                sen = st.text_input("Senha:", type="password")
                if st.form_submit_button("Finalizar"):
                    if n and sen:
                        if salvar_novo_usuario([n, tel, minis, str(nasc), sen, 1, "Plano Anual"]):
                            st.success("Sucesso! Faça Login.")
                        else: st.error("Erro ao salvar.")

    else:
        u = st.session_state.usuario
        df_l = carregar_dados("Leitura")
        df_progresso = carregar_dados("Progresso") # Importante: Aba "Progresso" na planilha

        if not df_l.empty:
            lista_planos = df_l['plano'].unique()
            plano_sel = st.selectbox("Escolha seu Plano:", lista_planos, key="sel_plano")
            
            # --- BUSCA O DIA GRAVADO NA PLANILHA ---
            dia_p = 1
            if not df_progresso.empty:
                # Normaliza colunas do progresso para evitar erro de busca
                df_progresso.columns = [str(c).lower().strip() for c in df_progresso.columns]
                prog_user = df_progresso[(df_progresso['usuario'] == u) & (df_progresso['plano'] == plano_sel)]
                if not prog_user.empty:
                    dia_p = int(prog_user.iloc[0]['dia_atual'])

            # Filtro do Conteúdo
            dados_plano = df_l[df_l['plano'] == plano_sel].copy()
            dados_plano['dia'] = pd.to_numeric(dados_plano['dia'], errors='coerce')
            l_hoje = dados_plano[dados_plano['dia'] == dia_p]
            
            if not l_hoje.empty:
                l = l_hoje.iloc[0]
                st.markdown(f"### 📍 {plano_sel} - Dia {dia_p}")
                
                # Layout Referência
                st.markdown(f"""
                    <div style="background: rgba(10, 61, 98, 0.4); padding: 20px; border-radius: 15px; border-left: 5px solid #00b894; margin-bottom: 20px;">
                        <h4 style="margin:0; color:#00b894;">📖 Referência:</h4>
                        <p style="font-size: 1.4em; margin-top: 10px;">{l.get('referencia', '---')}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.info(f"💡 **Meditação:** {l.get('resumo_para_meditacao', '---')}")
                
                # --- BOTÃO QUE GRAVA NA PLANILHA ---
                if st.button("✅ Concluí a leitura de hoje!", use_container_width=True):
                    # Chamamos a função de atualização (certifique-se que ela está no topo do código)
                    if atualizar_progresso_planilha(u, plano_sel, dia_p + 1):
                        st.balloons()
                        st.success("Progresso salvo!")
                        st.rerun()
            else:
                st.success(f"🎉 Plano {plano_sel} concluído!")
                if st.button("Reiniciar este Plano"):
                    atualizar_progresso_planilha(u, plano_sel, 1)
                    st.rerun()

        st.divider()
        if st.button("Sair da conta"):
            st.session_state.usuario = None
            st.rerun()
