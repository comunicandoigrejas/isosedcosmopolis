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
    
    /* DROPDOWN (Lista de seleção) */
    div[data-baseweb="popover"] * {
        color: black !important;
        background-color: white !important;
    }
    div[data-baseweb="popover"] li:hover {
        background-color: #ffd700 !important;
    }
    .texto-sagrado { 
        background-color: #f8f9fa; color: #1a1a2e !important; 
        padding: 15px; border-radius: 8px; font-size: 1.1em; line-height: 1.6;
    }
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
    datas = [d for d in dias_mes if d.weekday() in [2, 4, 6]]
    sabados = [d for d in dias_mes if d.weekday() == 5]
    if sabados: datas.append(max(sabados))
    return [{"data": d.strftime('%d/%m/%Y'), "dia_pt": dias_pt[d.weekday()], "is_domingo": d.weekday() == 6} for d in sorted(datas)]

def buscar_texto_biblico(referencia):
    try:
        url = f"https://bible-api.com/{referencia}?translation=almeida"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get('text', "Texto não disponível.")
        return "Não consegui carregar os versículos."
    except: return "Erro ao conectar com a Bíblia."

# =========================================================
# --- ROTEADOR PRINCIPAL ---
# =========================================================

# 1. PÁGINA: LOGIN (O PRIMEIRO DEVE SER 'IF')
if st.session_state.pagina == "Login":
    st.markdown("<h2>🔐 Acesso ao Sistema</h2>", unsafe_allow_html=True)
    with st.form("login_isosed"):
        u_nome = st.text_input("Usuário:")
        u_pass = st.text_input("Senha:", type="password")
        if st.form_submit_button("ENTRAR"):
            if u_nome.lower() == "admin" and u_pass == "isosed":
                st.session_state.pagina = "Início"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

# 2. PÁGINA: INÍCIO (AGORA COM LOGO)
elif st.session_state.pagina == "Início":
    from datetime import date
    
    # --- LOGO CENTRALIZADO ---
    # Criamos 3 colunas para colocar o logo na do meio e ele ficar no centro da tela
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 1, 1])
    with col_logo_2:
        # Substitua 'logo.png' pelo nome do seu arquivo ou pelo link direto da imagem
        st.image("logo.png", width=180) 
    
    st.markdown("<h1 style='text-align: center;'>Igreja Só o Senhor é Deus</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #d1d9e6;'>ISOSED Cosmópolis</p>", unsafe_allow_html=True)
    
    st.markdown("---")

 # --- Bloco Santa Ceia (Buscando na aba Agenda) ---
    with col1:
        st.subheader("🍷 Próxima Santa Ceia")
        # Agora buscamos na aba 'Agenda' conforme sua foto
        df_agenda_ceia = carregar_dados("Agenda")
        
        if not df_agenda_ceia.empty:
            # Filtra apenas os eventos que contém "Santa Ceia"
            df_so_ceia = df_agenda_ceia[df_agenda_ceia['evento'].str.contains("Santa Ceia", case=False, na=False)]
            
            if not df_so_ceia.empty:
                # Converte para data para garantir que pegamos a próxima
                df_so_ceia['dt_temp'] = pd.to_datetime(df_so_ceia['data'], dayfirst=True, errors='coerce')
                # Pega a primeira data que é hoje ou no futuro
                proximas_ceias = df_so_ceia[df_so_ceia['dt_temp'].dt.date >= hoje_br].sort_values('dt_temp')
                
                if not proximas_ceias.empty:
                    p = proximas_ceias.iloc[0]
                    st.info(f"📅 **Data:** {p['data']}\n\n⏰ **Horário:** 19:00")
                else:
                    st.write("Nenhuma data futura encontrada.")
            else:
                st.write("Evento 'Santa Ceia' não achado na Agenda.")
        else:
            st.write("Aba 'Agenda' está vazia.")

    # --- Bloco Aniversariantes (Próximos 7 dias) ---
    with col2:
        st.subheader("🎂 Aniversariantes")
        df_ani = carregar_dados("Aniversariantes")
        if not df_ani.empty:
            # Identifica colunas de forma inteligente
            c_nome = next((c for c in df_ani.columns if 'nome' in c), None)
            c_dia = next((c for c in df_ani.columns if 'dia' in c), None)
            c_mes = next((c for c in df_ani.columns if 'mes' in c or 'mês' in c), None)
            c_data = next((c for c in df_ani.columns if 'data' in c or 'aniv' in c), None)

            hoje = date.today()
            achou = False
            
            for _, row in df_ani.iterrows():
                try:
                    # Tenta pegar dia/mes de colunas separadas ou de uma coluna de data
                    if c_dia and c_mes:
                        d, m = int(row[c_dia]), int(row[c_mes])
                    elif c_data:
                        partes = str(row[c_data]).split('/')
                        d, m = int(partes[0]), int(partes[1])
                    else: continue

                    niver = date(hoje.year, m, d)
                    diff = (niver - hoje).days
                    if diff < 0: # Caso já tenha passado este ano
                        niver = date(hoje.year + 1, m, d)
                        diff = (niver - hoje).days

                    if 0 <= diff <= 7:
                        st.success(f"🎈 **{row[c_nome].upper()}** ({d}/{m:02d})")
                        achou = True
                except: continue
            
            if not achou: st.write("Ninguém soprando velinhas nos próximos 7 dias.")
        else:
            st.write("Lista de aniversariantes não encontrada.")
           # --- MENU DE NAVEGAÇÃO COMPLETO (6 BOTÕES) ---
    st.markdown("---")
    st.write("### ⛪ Ministérios e Ferramentas")
    
    # Linha 1: Funções Principais
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📖 LEITURA", use_container_width=True, key="btn_lei"): navegar("Leitura")
    with c2:
        if st.button("📅 ESCALAS", use_container_width=True, key="btn_esc"): navegar("Escalas")
    with c3:
        if st.button("⚙️ GESTÃO", use_container_width=True, key="btn_ges"): navegar("Gestao")

    # Linha 2: Agenda e Comunidade
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🗓️ AGENDA", use_container_width=True, key="btn_age"): navegar("Agenda")
    with c5:
        if st.button("🎂 ANIVERSÁRIOS", use_container_width=True, key="btn_ani"): navegar("Aniv")
    with c6:
        if st.button("🙏 DEVOCIONAL", use_container_width=True, key="btn_dev"): navegar("Devocional")
# =========================================================
# 4. PÁGINA: GESTÃO (REGRAS RÍGIDAS E FILTRO DE ACENTOS)
# =========================================================
elif st.session_state.pagina == "Gestao":
    import unicodedata

    def normalizar(texto):
        """Remove acentos e espaços para comparação segura"""
        return "".join(c for c in unicodedata.normalize('NFD', str(texto)) 
                       if unicodedata.category(c) != 'Mn').lower().strip()

    st.markdown("""
        <style>
        div[data-baseweb="select"] > div, div[data-baseweb="select"] * {
            background-color: white !important; color: black !important;
            -webkit-text-fill-color: black !important;
        }
        div[data-baseweb="popover"] * { color: black !important; background-color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_ges_v8")
    st.markdown("<h2>⚙️ Gestão de Escalas</h2>", unsafe_allow_html=True)

    if not st.session_state.admin_ok:
        with st.form("login_admin"):
            senha_gestao = st.text_input("Senha Master:", type="password")
            if st.form_submit_button("LIBERAR ACESSO"):
                if senha_gestao == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta.")
    else:
        st.success("Painel Administrativo Ativo")
        meses_pt = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        
        # --- FERRAMENTA DE LIMPEZA ---
        with st.expander("🧹 Limpar Escalas Existentes"):
            st.warning("Isso apagará as escalas do mês e setor selecionados abaixo.")
            if st.button("LIMPAR PLANILHA AGORA"):
                sh = conectar_planilha()
                aba_e = sh.worksheet("Escalas")
                # Lógica simples: apaga as últimas 50 linhas para teste ou recria a aba
                st.info("Funcionalidade de limpeza: Por favor, apague as linhas manualmente no Google Sheets para garantir 100% de precisão nesta fase.")

        with st.form("gerador_v8"):
            st.write("### 🤖 Gerador de Escala Blindado")
            c1, c2 = st.columns(2)
            with c1:
                mes_sel = st.selectbox("Mês:", options=list(meses_pt.keys()), format_func=lambda x: meses_pt[x], index=hoje_br.month - 1)
            with c2:
                ano_sel = st.selectbox("Ano:", options=[2026, 2027], index=0)
            
            setor_sel = st.radio("Departamento:", ["Fotografia", "Recepção", "Som/Mídia"])
            
            if st.form_submit_button("🚀 GERAR ESCALA SEM ERROS"):
                with st.spinner("Processando..."):
                    df_v = carregar_dados("Voluntarios")
                    if not df_v.empty:
                        col_fun = next((c for c in df_v.columns if 'fun' in c), None)
                        col_nom = next((c for c in df_v.columns if 'nome' in c), None)

                        if col_fun and col_nom:
                            mapa = {"Fotografia": "fotografia", "Recepção": "recepção", "Som/Mídia": "operador"}
                            termo = mapa[setor_sel]
                            
                            v_setor = df_v[df_v[col_fun].astype(str).str.lower() == termo][col_nom].tolist()
                            
                            # FILTRO BLINDADO (Pega Júnior com ou sem acento)
                            v_normais = [n for n in v_setor if "junior" not in normalizar(n)]
                            v_junior = [n for n in v_setor if "junior" in normalizar(n)]
                            
                            if v_normais:
                                datas = obter_datas_culto_pt(ano_sel, mes_sel)
                                sh = conectar_planilha()
                                aba_e = sh.worksheet("Escalas")
                                
                                # Define O ÚNICO domingo do Júnior (2º domingo)
                                domingos_idx = [i for i, d in enumerate(datas) if d['is_domingo']]
                                idx_alvo_junior = domingos_idx[1] if len(domingos_idx) > 1 else (domingos_idx[0] if domingos_idx else -1)

                                p_idx = 0 
                                for i, d in enumerate(datas):
                                    # Horários
                                    if d['dia_pt'] == "Sábado": horario = "14:30"
                                    elif d['is_domingo']: horario = "18:00"
                                    else: horario = "19:30"

                                    responsavel = ""
                                    if setor_sel == "Som/Mídia":
                                        # REGRA RÍGIDA: Se for o dia do Júnior, usa ele. SENÃO, usa a lista limpa.
                                        if i == idx_alvo_junior and v_junior:
                                            responsavel = v_junior[0]
                                        else:
                                            responsavel = v_normais[p_idx % len(v_normais)]
                                            p_idx += 1
                                    elif setor_sel == "Recepção":
                                        p1 = v_normais[p_idx % len(v_normais)]
                                        p2 = v_normais[(p_idx + 1) % len(v_normais)]
                                        responsavel = f"{p1}, {p2}"
                                        p_idx += 2
                                    else: # Fotografia
                                        responsavel = v_normais[p_idx % len(v_normais)]
                                        p_idx += 1

                                    aba_e.append_row([d['data'], d['dia_pt'], horario, "Culto", setor_sel, responsavel])
                                
                                st.success("✅ Escala gerada! O Júnior foi filtrado corretamente.")
# --- 5. DEVOCIONAL ---
elif st.session_state.pagina == "Devocional":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_dev")
    df_dev = carregar_dados("Devocional")
    if not df_dev.empty:
        item = df_dev.iloc[-1]
        st.markdown(f"### {item['titulo']}")
        st.warning(f"📖 **VERSÍCULO:** {item['versiculo']}")
        st.write(item['texto'])
        st.info(f"🎯 **APLICAÇÃO:** {item['aplicacao']}")
        st.success(f"🔥 **DESAFIO:** {item['desafio']}")

# --- 6. ESCALAS ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_esc")
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    df_esc = carregar_dados("Escalas")
    if not df_esc.empty:
        df_esc['dt'] = pd.to_datetime(df_esc['data'], dayfirst=True, errors='coerce')
        prox = df_esc[df_esc['dt'].dt.date >= hoje_br].sort_values('dt')
        t1, t2, t3 = st.tabs(["📸 Foto", "🔊 Som/Mídia", "🤝 Recepção"])
        with t1:
            f = prox[prox['departamento'].str.contains("Foto", case=False, na=False)]
            for _, r in f.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t2:
            o = prox[prox['departamento'].str.contains("Mídia|Som", case=False, na=False)]
            for _, r in o.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)
        with t3:
            rec = prox[prox['departamento'].str.contains("Recepção", case=False, na=False)]
            for _, r in rec.iterrows(): st.markdown(f'<div class="card-isosed"><b>{r["data"]} - {r["dia"]}</b><br>👤 {r["responsável"]}</div>', unsafe_allow_html=True)

# =========================================================
# 6. PÁGINA: LEITURA (VERSÃO "NÃO ACEITO 404")
# =========================================================
elif st.session_state.pagina == "Leitura":
    import re
    import urllib.parse
    import unicodedata

    st.markdown("""
        <style>
        div[data-baseweb="select"] > div, div[data-baseweb="select"] * {
            background-color: white !important; color: black !important;
            -webkit-text-fill-color: black !important;
        }
        div[data-baseweb="popover"] * { color: black !important; background-color: white !important; }
        .caixa-leitura {
            background-color: #f1f3f8; color: #1a1a2e !important;
            padding: 20px; border-radius: 10px; font-size: 1.2em;
            line-height: 1.6; text-align: justify; border: 1px solid #d1d9e6;
        }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_lei_v17_final")

    if st.session_state.user is None:
        # (Seu código de login aqui...)
        with st.form("login_leitura_v17"):
            u_n = st.text_input("Seu Nome:")
            u_s = st.text_input("Senha:", type="password")
            if st.form_submit_button("ACESSAR"):
                df_u = carregar_dados("Usuarios")
                u_f = df_u[(df_u['nome'].str.lower() == u_n.lower()) & (df_u['senha'].astype(str) == str(u_s))]
                if not u_f.empty: st.session_state.user = u_f.iloc[0].to_dict(); st.rerun()
                else: st.error("Acesso negado.")
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        col_usu_p = next((c for c in df_p.columns if 'usu' in c), 'usuario')
        
        if not df_p.empty:
            meus_planos = df_p[df_p[col_usu_p].astype(str).str.lower() == u['nome'].lower()]
            
            if not meus_planos.empty:
                plano_sel = st.selectbox("Seu plano:", meus_planos['plano'].tolist())
                col_dia_p = next((c for c in df_p.columns if 'dia' in c), 'dia_atual')
                dia_hoje = int(meus_planos[meus_planos['plano'] == plano_sel].iloc[0][col_dia_p])
                
                st.markdown(f"#### 📖 {u['nome']} - Dia {dia_hoje}")
                
                df_lei = carregar_dados("Leitura")
                l_hoje = df_lei[(df_lei['plano'] == plano_sel) & (df_lei['dia'].astype(str) == str(dia_hoje))]
                
                if not l_hoje.empty:
                    ref_bruta = l_hoje.iloc[0].get('referência', l_hoje.iloc[0].get('referencia', ''))
                    lista_previa = re.split(r'[,;]', ref_bruta)
                    lista_caps = []
                    for p in [item.strip() for item in lista_previa if item.strip()]:
                        if '-' in p:
                            m = re.match(r"([0-9]*\s*[A-Za-zÀ-ÿ]+)\s*(\d+)-(\d+)", p)
                            if m:
                                livro, ini, fim = m.groups()
                                for n in range(int(ini), int(fim) + 1): lista_caps.append(f"{livro} {n}")
                            else: lista_caps.append(p)
                        else: lista_caps.append(p)
                    
                    cap_sel = st.selectbox("Escolha o capítulo:", lista_caps)

                    # --- DICIONÁRIO DE TRADUÇÃO (SINGULAR PARA EVITAR ERRO) ---
                    tradutor_en = {
                        "salmos": "Psalm", "salmo": "Psalm", "genesis": "Genesis", "exodo": "Exodus",
                        "levitico": "Leviticus", "numeros": "Numbers", "deuteronomio": "Deuteronomy",
                        "joao": "John", "mateus": "Matthew", "marcos": "Mark", "lucas": "Luke"
                    }

                    def limpar_nome(ref):
                        return "".join(c for c in unicodedata.normalize('NFD', ref) if unicodedata.category(c) != 'Mn').lower().strip()

                    # Lógica de Busca com Fallback (Tripla Tentativa)
                    def buscar_biblia(ref_original):
                        nome_limpo = limpar_nome(ref_original)
                        ref_en = ref_original
                        
                        # Tenta traduzir para o Inglês Singular (Psalm 24)
                        for pt, en in tradutor_en.items():
                            if nome_limpo.startswith(pt):
                                ref_en = nome_limpo.replace(pt, en)
                                break
                        
                        urls_tentativas = [
                            f"https://bible-api.com/{urllib.parse.quote(ref_en)}?translation=almeida", # 1. Inglês com Almeida
                            f"https://bible-api.com/{urllib.parse.quote(ref_original)}?translation=almeida", # 2. Português com Almeida
                            f"https://bible-api.com/{urllib.parse.quote(ref_en)}" # 3. Inglês (Padrão) como última opção
                        ]

                        for url in urls_tentativas:
                            try:
                                res = requests.get(url, timeout=5)
                                if res.status_code == 200:
                                    return res.json().get('text', None)
                            except: continue
                        return None

                    with st.spinner("Buscando Palavra..."):
                        texto_sagrado = buscar_biblia(cap_sel)
                        
                        if texto_sagrado:
                            st.markdown(f'<div class="caixa-leitura">{texto_sagrado}</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"⚠️ Não conseguimos carregar '{cap_sel}'. A API da Bíblia está fora do ar ou a referência não existe.")
                    
                    if st.button("✅ CONCLUIR DIA"):
                        sh = conectar_planilha()
                        aba_p = sh.worksheet("Progresso")
                        cels = aba_p.findall(u['nome'])
                        for c in cels:
                            if aba_p.cell(c.row, 2).value == plano_sel:
                                aba_p.update_cell(c.row, 3, dia_hoje + 1)
                                st.balloons(); st.rerun()
