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

# =========================================================
# 2. PÁGINA: INÍCIO (NAVEGAÇÃO INSTANTÂNEA DE 1 CLIQUE)
# =========================================================
elif st.session_state.pagina == "Início":
    from datetime import date
    import base64

    # --- ESCONDER BARRA SUPERIOR E MENUS ---
    st.markdown("""
        <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

    # --- LOGO CENTRALIZADO ---
    def set_centered_logo(png_file, width=180):
        try:
            with open(png_file, "rb") as f:
                data = f.read()
                bin_str = base64.b64encode(data).decode()
                st.markdown(
                    f"""
                    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
                        <img src="data:image/png;base64,{bin_str}" width="{width}px">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        except:
            st.markdown("<h3 style='text-align:center;'>⛪</h3>", unsafe_allow_html=True)

    set_centered_logo("logo igreja.png", width=180)
    st.markdown("<p style='text-align: center; color: #d1d9e6; font-weight: bold;'>ISOSED Cosmópolis</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # --- INFO: SANTA CEIA E ANIVERSARIANTES ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🍷 Próxima Santa Ceia")
        df_agenda = carregar_dados("Agenda")
        if not df_agenda.empty:
            df_so_ceia = df_agenda[df_agenda['evento'].str.contains("Santa Ceia", case=False, na=False)]
            if not df_so_ceia.empty:
                df_so_ceia['dt_temp'] = pd.to_datetime(df_so_ceia['data'], dayfirst=True, errors='coerce')
                prox = df_so_ceia[df_so_ceia['dt_temp'].dt.date >= hoje_br].sort_values('dt_temp')
                if not prox.empty:
                    p = prox.iloc[0]
                    st.info(f"📅 **Data:** {p['data']}\n\n⏰ **Horário:** 18:00")
                else: st.write("A definir.")
            else: st.write("Santa Ceia não agendada.")

    with col2:
        st.subheader("🎂 Aniversariantes")
        df_ani = carregar_dados("Aniversariantes")
        if not df_ani.empty:
            c_nome = next((c for c in df_ani.columns if 'nome' in c), None)
            c_dia = next((c for c in df_ani.columns if 'dia' in c), None)
            c_mes = next((c for c in df_ani.columns if 'mes' in c or 'mês' in c), None)
            hoje = date.today()
            achou = False
            for _, row in df_ani.iterrows():
                try:
                    d, m = int(row[c_dia]), int(row[c_mes])
                    niver = date(hoje.year, m, d)
                    diff = (niver - hoje).days
                    if diff < 0: niver = date(hoje.year + 1, m, d); diff = (niver - hoje).days
                    if 0 <= diff <= 7:
                        st.success(f"🎈 **{row[c_nome].upper()}** ({d}/{m:02d})")
                        achou = True
                except: continue
            if not achou: st.write("Ninguém nos próximos 7 dias.")

    # --- MENU DE NAVEGAÇÃO (BOTÕES COM ON_CLICK PARA 1 CLIQUE REAL) ---
    st.markdown("---")
    st.write("### ⛪ Ministérios e Ferramentas")
    
    m1, m2, m3 = st.columns(3)
    # Aqui usamos 'on_click' para a mudança ser imediata
    with m1:
        st.button("📖 LEITURA", use_container_width=True, on_click=navegar, args=("Leitura",), key="btn_lei")
    with m2:
        st.button("📅 ESCALAS", use_container_width=True, on_click=navegar, args=("Escalas",), key="btn_esc")
    with m3:
        st.button("⚙️ GESTÃO", use_container_width=True, on_click=navegar, args=("Gestao",), key="btn_ges")

    m4, m5, m6 = st.columns(3)
    with m4:
        st.button("🗓️ AGENDA", use_container_width=True, on_click=navegar, args=("Agenda",), key="btn_age")
    with m5:
        st.button("🎂 ANIVERSÁRIOS", use_container_width=True, on_click=navegar, args=("Aniv",), key="btn_ani")
    with m6:
        st.button("🙏 DEVOCIONAL", use_container_width=True, on_click=navegar, args=("Devocional",), key="btn_dev")

        # =========================================================
# 3. PÁGINA: ANIVERSARIANTES (VERSÃO BLINDADA)
# =========================================================
elif st.session_state.pagina == "Aniv":
    # Botão Voltar com 1 clique real
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_aniv_v2")
    
    st.markdown("<h2>🎂 Mural de Aniversariantes</h2>", unsafe_allow_html=True)
    
    df_aniv = carregar_dados("Aniversariantes")
    
    # Criamos as abas para cada mês
    nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    abas_mes = st.tabs(nomes_meses)
    
    if not df_aniv.empty:
        # Busca inteligente de colunas
        c_nome = next((c for c in df_aniv.columns if 'nome' in c), None)
        c_dia = next((c for c in df_aniv.columns if 'dia' in c), None)
        c_mes = next((c for c in df_aniv.columns if 'mes' in c or 'mês' in c), None)
        c_data = next((c for c in df_aniv.columns if 'data' in c or 'aniv' in c), None)

        if c_nome:
            for i, aba in enumerate(abas_mes):
                with aba:
                    num_mes_alvo = i + 1
                    lista_do_mes = []

                    # Processa cada linha da planilha
                    for _, r in df_aniv.iterrows():
                        try:
                            d, m = None, None
                            
                            # Opção 1: Colunas separadas (Dia e Mês)
                            if c_dia and c_mes and pd.notna(r[c_dia]) and pd.notna(r[c_mes]):
                                d, m = int(r[c_dia]), int(r[c_mes])
                            
                            # Opção 2: Coluna única de Data (DD/MM)
                            elif c_data and pd.notna(r[c_data]):
                                partes = str(r[c_data]).split('/')
                                d, m = int(partes[0]), int(partes[1])
                            
                            # Se o mês da pessoa for o mês da aba atual, adiciona na lista
                            if m == num_mes_alvo:
                                lista_do_mes.append({"dia": d, "nome": str(r[c_nome]).upper()})
                        except:
                            continue

                    # Exibe os aniversariantes do mês ordenados por dia
                    if lista_do_mes:
                        # Ordena a lista pelo dia antes de mostrar
                        lista_do_mes = sorted(lista_do_mes, key=lambda x: x['dia'])
                        for pessoa in lista_do_mes:
                            st.markdown(f"""
                                <div class="card-isosed" style="border-left: 5px solid #ffd700;">
                                    <b>🎁 Dia {pessoa['dia']:02d}</b> — {pessoa['nome']}
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(f"Sem aniversariantes em {nomes_meses[i]}.")
        else:
            st.error("Erro: A coluna 'NOME' não foi encontrada na aba Aniversariantes.")
    else:
        st.warning("A aba 'Aniversariantes' está vazia ou não foi encontrada.")
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
                if senha_gestao == "MEUPAINAODEIXA":
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

                                # =========================================================
# 4. PÁGINA: AGENDA (VERSÃO BLINDADA CONTRA ERROS DE DATA)
# =========================================================
elif st.session_state.pagina == "Agenda":
    # Botão Voltar com 1 clique real
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_age_v2")
    
    st.markdown("<h2>🗓️ Agenda de Eventos 2026</h2>", unsafe_allow_html=True)
    
    df_agenda = carregar_dados("Agenda")
    
    # Criamos as abas para cada mês
    nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    abas_mes = st.tabs(nomes_meses)
    
    if not df_agenda.empty:
        # Busca inteligente de colunas
        c_data = next((c for c in df_agenda.columns if 'data' in c), None)
        c_evento = next((c for c in df_agenda.columns if 'evento' in c), None)

        if c_data and c_evento:
            for i, aba in enumerate(abas_mes):
                with aba:
                    num_mes_alvo = i + 1
                    lista_eventos_mes = []

                    # Processa cada linha da planilha individualmente
                    for _, r in df_agenda.iterrows():
                        try:
                            # Tenta converter a data da planilha (DD/MM/AAAA)
                            data_str = str(r[c_data]).strip()
                            data_dt = pd.to_datetime(data_str, dayfirst=True, errors='coerce')
                            
                            # Se a data for válida e do mês da aba atual
                            if pd.notna(data_dt) and data_dt.month == num_mes_alvo:
                                lista_eventos_mes.append({
                                    "data_formatada": data_str,
                                    "data_obj": data_dt,
                                    "evento": str(r[c_evento]).upper()
                                })
                        except:
                            continue

                    # Exibe os eventos ordenados por dia
                    if lista_eventos_mes:
                        # Ordena a lista pela data
                        lista_eventos_mes = sorted(lista_eventos_mes, key=lambda x: x['data_obj'])
                        for item in lista_eventos_mes:
                            st.markdown(f"""
                                <div class="card-isosed" style="border-left: 5px solid #00d4ff; margin-bottom: 10px;">
                                    <b style="color:#00d4ff;">📅 {item['data_formatada']}</b><br>
                                    <span style="font-size: 1.1em;">{item['evento']}</span>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info(f"Nenhum evento agendado para {nomes_meses[i]}.")
        else:
            st.error("Erro: Colunas 'DATA' ou 'EVENTO' não encontradas na aba Agenda.")
    else:
        st.warning("A aba 'Agenda' está vazia no Google Sheets.")
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
