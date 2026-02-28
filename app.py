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

# --- 1. INÍCIO ---
if st.session_state.pagina == "Início":
    col_l1, col_l2, col_l3 = st.columns([1, 1.2, 1])
    with col_l2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    df_ag = carregar_dados("Agenda")
    prox = "A definir"
    if not df_ag.empty:
        df_ag['dt_p'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceia = df_ag[df_ag['evento'].str.contains("Santa Ceia", case=False, na=False)].sort_values('dt_p')
        if not ceia.empty: prox = ceia.iloc[0]['data']
    st.markdown(f'<div class="card-isosed" style="text-align:center;">🍇 PRÓXIMA SANTA CEIA<br><b style="font-size:1.3em; color:#ffd700;">{prox} às 18h00</b></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",))
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",))
        st.button("⚙️ Gestão", on_click=navegar, args=("Gestao",))
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",))
        st.button("📖 Devocional", on_click=navegar, args=("Devocional",))
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",))

# --- 2. AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_agenda")
    st.markdown("<h2>🗓️ Agenda ISOSED 2026</h2>", unsafe_allow_html=True)
    df_agenda = carregar_dados("Agenda")
    abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    
    if not df_agenda.empty:
        df_agenda['data_dt'] = pd.to_datetime(df_agenda['data'], dayfirst=True, errors='coerce')
        for i, aba in enumerate(abas):
            with aba:
                mes_atual = i + 1
                eventos_mes = df_agenda[df_agenda['data_dt'].dt.month == mes_atual].sort_values('data_dt')
                if not eventos_mes.empty:
                    for _, linha in eventos_mes.iterrows():
                        st.markdown(f'<div class="card-isosed"><b style="color:#ffd700;">{linha["data"]}</b><br>{linha["evento"]}</div>', unsafe_allow_html=True)
                else: st.info("Sem eventos.")

# --- 3. ANIVERSÁRIOS ---
elif st.session_state.pagina == "Aniv":
    st.button("⬅️ VOLTAR PARA O INÍCIO", on_click=navegar, args=("Início",), key="voltar_aniv")
    st.markdown("<h2>🎂 Aniversariantes</h2>", unsafe_allow_html=True)
    df_aniv = carregar_dados("Aniversariantes")
    abas_mes = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
    
    if not df_aniv.empty:
        col_mes = next((c for c in df_aniv.columns if 'mes' in c or 'mês' in c), None)
        col_dia = next((c for c in df_aniv.columns if 'dia' in c), None)
        col_nome = next((c for c in df_aniv.columns if 'nome' in c), None)
        if col_mes and col_dia and col_nome:
            for i, aba in enumerate(abas_mes):
                with aba:
                    num_mes = i + 1
                    lista_mes = df_aniv[df_aniv[col_mes].astype(int) == num_mes].sort_values(col_dia)
                    if not lista_mes.empty:
                        for _, r in lista_mes.iterrows():
                            st.markdown(f'<div class="card-isosed">🎁 Dia {r[col_dia]} - {r[col_nome]}</div>', unsafe_allow_html=True)
                    else: st.info("Sem aniversariantes.")

# =========================================================
# 4. PÁGINA: GESTÃO (REGRAS RÍGIDAS - JÚNIOR SÓ 1X NO DOMINGO)
# =========================================================
elif st.session_state.pagina == "Gestao":
    st.markdown("""
        <style>
        div[data-baseweb="select"] > div, div[data-baseweb="select"] * {
            background-color: white !important;
            color: black !important;
            -webkit-text-fill-color: black !important;
        }
        div[data-baseweb="popover"] * { color: black !important; background-color: white !important; }
        </style>
    """, unsafe_allow_html=True)

    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_ges_junior_v6")
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
        
        with st.form("gerador_rodizio_blindado"):
            st.write("### 🤖 Gerador de Escala Inteligente")
            c1, c2 = st.columns(2)
            with c1:
                mes_sel = st.selectbox("Mês:", options=list(meses_pt.keys()), format_func=lambda x: meses_pt[x], index=hoje_br.month - 1)
            with c2:
                ano_sel = st.selectbox("Ano:", options=[2026, 2027], index=0)
            
            setor_sel = st.radio("Selecione o Departamento:", ["Fotografia", "Recepção", "Som/Mídia"])
            
            if st.form_submit_button(f"🚀 GERAR ESCALA"):
                with st.spinner("Aplicando regras rígidas de rodízio..."):
                    df_v = carregar_dados("Voluntarios")
                    if not df_v.empty:
                        col_funcao = next((c for c in df_v.columns if 'fun' in c), None)
                        col_nome = next((c for c in df_v.columns if 'nome' in c), None)

                        if col_funcao and col_nome:
                            mapa = {"Fotografia": "fotografia", "Recepção": "recepção", "Som/Mídia": "operador"}
                            termo = mapa[setor_sel]
                            
                            # LISTAS SEPARADAS
                            todos_nomes = df_v[df_v[col_funcao].astype(str).str.lower() == termo][col_nome].tolist()
                            v_normais = [n for n in todos_nomes if "junior" not in n.lower()]
                            v_junior = [n for n in todos_nomes if "junior" in n.lower()]
                            
                            if v_normais or v_junior:
                                datas = obter_datas_culto_pt(ano_sel, mes_sel)
                                sh = conectar_planilha()
                                aba_e = sh.worksheet("Escalas")
                                
                                # Identifica os domingos para o Júnior
                                domingos_idx = [i for i, d in enumerate(datas) if d['is_domingo']]
                                # Júnior fica rigorosamente com o 2º domingo (se existir) ou o único disponível
                                idx_alvo_junior = domingos_idx[1] if len(domingos_idx) > 1 else (domingos_idx[0] if domingos_idx else -1)

                                p_idx = 0 # Ponteiro exclusivo para o rodízio normal
                                
                                for i, d in enumerate(datas):
                                    # Definição de horários padrão ISOSED
                                    if d['dia_pt'] == "Sábado": horario = "14:30"
                                    elif d['is_domingo']: horario = "18:00"
                                    else: horario = "19:30"

                                    responsavel = ""

                                    if setor_sel == "Som/Mídia":
                                        # REGRA RÍGIDA DO JÚNIOR
                                        if i == idx_alvo_junior and v_junior:
                                            responsavel = v_junior[0]
                                            # Aqui o p_idx NÃO aumenta para manter a sequência dos outros
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
                                
                                st.success(f"✅ Escala de {setor_sel} gerada com sucesso! Júnior alocado apenas no domingo dia {datas[idx_alvo_junior]['data'] if idx_alvo_junior != -1 else 'N/A'}.")
                            else: st.warning("Nenhum voluntário encontrado.")
                        else: st.error("Erro nas colunas da planilha.")
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

# --- 7. LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_lei_ok")
    if st.session_state.user is None:
        with st.form("login_nome"):
            st.markdown("### 🔐 Entrar no Plano")
            u_nome = st.text_input("Seu Nome:")
            u_pass = st.text_input("Senha:", type="password")
            if st.form_submit_button("ACESSAR"):
                df_u = carregar_dados("Usuarios")
                u_f = df_u[(df_u['nome'].str.lower() == u_nome.lower()) & (df_u['senha'].astype(str) == str(u_pass))]
                if not u_f.empty: st.session_state.user = u_f.iloc[0].to_dict(); st.rerun()
                else: st.error("Nome ou senha incorretos.")
    else:
        u = st.session_state.user
        df_p = carregar_dados("Progresso")
        meus_planos = df_p[df_p['usuario'].str.lower() == u['nome'].lower()]
        if not meus_planos.empty:
            plano_ativo = st.selectbox("Selecione o Plano:", meus_planos['plano'].tolist())
            dados_p = meus_planos[meus_planos['plano'] == plano_ativo].iloc[0]
            dia_hoje = int(dados_p['dia_atual'])
            st.markdown(f"#### 📖 {u['nome']} - Dia {dia_hoje}")
            df_lei = carregar_dados("Leitura")
            l_data = df_lei[(df_lei['plano'] == plano_ativo) & (df_lei['dia'].astype(str) == str(dia_hoje))]
            if not l_data.empty:
                ref_bruta = l_data.iloc[0].get('referência', l_data.iloc[0].get('referencia', ''))
                caps = [c.strip() for c in ref_bruta.split(',')]
                escolha_cap = st.selectbox("Capítulo para ler:", caps)
                with st.spinner("Carregando..."): txt = buscar_texto_biblico(escolha_cap)
                st.markdown(f'<div class="texto-sagrado">{txt}</div>', unsafe_allow_html=True)
                if st.button("✅ CONCLUIR DIA"):
                    sh = conectar_planilha()
                    aba_p = sh.worksheet("Progresso")
                    celulas = aba_p.findall(u['nome'])
                    for c in celulas:
                        if aba_p.cell(c.row, 2).value == plano_ativo:
                            aba_p.update_cell(c.row, 3, dia_hoje + 1)
                            st.success("Dia atualizado!")
                            st.rerun()
        if st.button("Sair da Conta"):
            st.session_state.user = None
            st.rerun()
