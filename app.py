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

# --- 1. CONFIGURAÇÃO E DATA ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# Inicializa a memória do App (Resolve o AttributeError)
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

def navegar(p):
    st.session_state.pagina = p

# --- 2. FUNÇÕES DE BANCO DE DADOS (Devem vir ANTES do uso) ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_p = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_p}/gviz/tq?tqx=out:csv&sheet={aba}"
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

# --- 1. ESTILO CSS (Coloque apenas UMA vez no topo) ---
st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, p, span { color: #FFFFFF !important; font-weight: 700 !important; }

    /* Quadros Amarelos dos Aniversariantes */
    .card-niver {
        background: rgba(255, 215, 0, 0.1) !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important; 
        padding: 12px !important;
        text-align: center !important;
        margin-bottom: 15px !important;
    }
    .niver-nome { font-size: 0.9em !important; font-weight: 900 !important; color: #ffd700 !important; text-transform: uppercase; }
    .niver-data { font-size: 1.1em !important; font-weight: bold !important; color: white !important; }
    
    /* Botões */
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important; background-color: #0a3d62 !important; border: 2px solid #3c6382 !important; border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ROTEADOR DE PÁGINAS (Garanta que só exista UM de cada) ---

if st.session_state.pagina == "Início":
    # Lógica do Contador
    if 'acesso_contado' not in st.session_state:
        try:
            sh_ac = conectar_planilha()
            aba_ac = sh_ac.worksheet("Acessos")
            total = int(aba_ac.acell('A2').value or 0)
            aba_ac.update_cell(2, 1, total + 1)
            st.session_state.acesso_contado = total + 1
        except: st.session_state.acesso_contado = "---"

    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    # QUADRO: NOSSOS CULTOS
    st.markdown("""
        <div style="background: rgba(10, 61, 98, 0.4); border: 1px solid #3c6382; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
            <h4 style="margin:0; color:#ffd700; text-align:center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom:10px;">🙏 Nossos Cultos</h4>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Segunda-feira</span> <b>Oração Ministerial 19h30</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Quarta-feira</span> <b>Ensino - 19h30</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Sexta-feira</span> <b>Libertação - 19h30</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Domingo</span> <b>Família - 18h00</b></div>
        </div>
    """, unsafe_allow_html=True)

    # QUADRO: PRÓXIMA SANTA CEIA (Busca na Agenda)
    df_ag = carregar_dados("Agenda")
    if not df_ag.empty:
        df_ag['data_dt'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        ceias = df_ag[df_ag['evento'].str.contains("Ceia", case=False, na=False)]
        prox = ceias[ceias['data_dt'].dt.date >= hoje_br].sort_values(by='data_dt')
        if not prox.empty:
            p_ceia = prox.iloc[0]['data_dt'].strftime('%d/%m/%Y')
            st.markdown(f"""
                <div style="background: linear-gradient(90deg, #b33939, #822727); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 25px; border: 2px solid #ff5252;">
                    <h3 style="margin:0; color: white !important;">🍞 PRÓXIMA SANTA CEIA: {p_ceia} 🍷</h3>
                </div>
            """, unsafe_allow_html=True)

    # QUADRO: ANIVERSARIANTES (Com quadro amarelo)
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        dom = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
        seg = dom + timedelta(days=8)
        aniv_f = [r for _, r in df_n.iterrows() if dom <= datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date() <= seg]
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    # MENU DE BOTÕES
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), use_container_width=True, key="btn_agenda")
        st.button("👥 Grupos", on_click=navegar, args=("Grupos",), use_container_width=True, key="btn_grupos")
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",), use_container_width=True, key="btn_aniversarios")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), use_container_width=True, key="btn_escalas")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), use_container_width=True, key="btn_meditar")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), use_container_width=True, key="btn_leitura")
    with c3:
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), use_container_width=True, key="btn_gestao_lider")

    # LOGO E CONTADOR
    if os.path.exists("logo igreja.png"):
        st.markdown("<br>", unsafe_allow_html=True)
        col_esq, col_centro, col_dir = st.columns([1, 2, 1])
        with col_centro:
            st.image("logo igreja.png", use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-size:0.8em; opacity:0.6;'>Acessos totais: {st.session_state.acesso_contado}</p>", unsafe_allow_html=True)

# --- 3. ABA AGENDA (Alinhada corretamente para abrir) ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="voltar_ag")
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    
    df_ag_view = carregar_dados("Agenda")
    if not df_ag_view.empty:
        df_ag_view['data_dt'] = pd.to_datetime(df_ag_view['data'], dayfirst=True, errors='coerce')
        meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        abas_mes = st.tabs(meses)
        for i, aba in enumerate(abas_mes):
            with aba:
                evs = df_ag_view[df_ag_view['data_dt'].dt.month == (i+1)].sort_values(by='data_dt')
                if not evs.empty:
                    for _, r in evs.iterrows():
                        st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid #0a3d62;"><b style="color:#ffd700;">{r["data_dt"].strftime("%d/%m")}</b> - {r.get("evento", "")}</div>', unsafe_allow_html=True)
                else:
                    st.info("Sem eventos programados para este mês.")

# --- 4. ABA ESCALAS (O que a Igreja vê) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="voltar_esc")
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    
    df_esc = carregar_dados("Escalas")
    if not df_esc.empty:
        df_esc['dt'] = pd.to_datetime(df_esc['Data'], dayfirst=True, errors='coerce')
        # Mostra apenas escalas de hoje em diante
        proximas = df_esc[df_esc['dt'].dt.date >= hoje_br].sort_values(by='dt')
        
        if not proximas.empty:
            for _, r in proximas.iterrows():
                st.markdown(f"""
                    <div style="background: rgba(255, 215, 0, 0.1); border: 2px solid #ffd700; border-radius: 15px; padding: 15px; margin-bottom: 15px;">
                        <span style="color: #ffd700; font-weight: bold;">{r['Data']} - {r['Dia']}</span><br>
                        <span style="font-size: 1.2em; font-weight: 900;">{r['Evento']}</span><br>
                        <hr style="margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);">
                        👤 <b>{r['Responsável']}</b><br>
                        📍 {r['Departamento']} | ⏰ {r['Horário']}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nenhuma escala futura encontrada.")
    else:
        st.warning("A planilha de escalas está vazia ou ainda não foi criada.")

# --- 5. ABA LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="voltar_lei")
    st.markdown("<h1>📜 Plano de Leitura Bíblica</h1>", unsafe_allow_html=True)
    st.info("Acompanhe aqui o plano de leitura para 2026.")
    # Adicione aqui o seu conteúdo específico de leitura (links, tabelas, etc.)

# --- 6. ABA GESTÃO (Painel do Líder - Acesso com Senha) ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="voltar_gest")
    st.markdown("<h1>⚙️ Painel de Gestão (Líderes)</h1>", unsafe_allow_html=True)

    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok = False

    if not st.session_state.admin_ok:
        with st.form("login_admin"):
            senha = st.text_input("Senha de Líder:", type="password")
            if st.form_submit_button("Acessar Painel"):
                if senha == "ISOSED2026": # Mude sua senha aqui
                    st.session_state.admin_ok = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
    else:
        st.success("Bem-vindo! Use as abas abaixo para gerar as escalas.")
        
        col1, col2 = st.columns(2)
        with col1: mes_sel = st.selectbox("Mês:", list(range(1, 13)), index=hoje_br.month - 1)
        with col2: ano_sel = st.number_input("Ano:", value=2026)

        tab_rec, tab_foto, tab_ops = st.tabs(["🤝 Recepção", "📸 Fotógrafos", "🔊 Operadores"])

        import calendar
        cal = calendar.Calendar()
        dias_mes = [d for sem in cal.monthdatescalendar(ano_sel, mes_sel) for d in sem if d.month == mes_sel]
        ultimo_sab = max([d for d in dias_mes if d.weekday() == 5])
        datas_alvo = [d for d in dias_mes if d.weekday() in [2, 4, 6] or d == ultimo_sab]
        datas_alvo.sort()

        # --- Lógica Recepção ---
        with tab_rec:
            if st.button("🤖 Gerar Escala Recepção"):
                equipe = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                res, idx = [], 0
                for d in datas_alvo:
                    p1, p2 = equipe[idx % 7], equipe[(idx + 1) % 7]
                    h = "14h30" if d == ultimo_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Recepção", "Responsável": f"{p1} e {p2}"})
                    idx += 2
                st.session_state.temp_escala = pd.DataFrame(res)

        # --- Lógica Fotógrafos ---
        with tab_foto:
            if st.button("🤖 Gerar Escala Fotógrafos"):
                equipe = ["Tiago", "Grazi"]
                res = []
                for i, d in enumerate(datas_alvo):
                    h = "14h30" if d == ultimo_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Fotografia", "Responsável": equipe[i % 2]})
                st.session_state.temp_escala = pd.DataFrame(res)

        # --- Lógica Operadores ---
        with tab_ops:
            if st.button("🤖 Gerar Escala Operadores"):
                p_geral, p_dom = ["Lucas", "Samuel", "Nicholas"], ["Júnior", "Lucas", "Samuel", "Nicholas"]
                res, ig, idom = [], 0, 0
                for d in datas_alvo:
                    op = p_dom[idom % 4] if d.weekday()==6 else p_geral[ig % 3]
                    if d.weekday()==6: idom +=1
                    else: ig += 1
                    h = "14h30" if d == ultimo_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Mídia (Som)", "Responsável": op})
                st.session_state.temp_escala = pd.DataFrame(res)

        # ÁREA DE SALVAMENTO
        if "temp_escala" in st.session_state:
            st.divider()
            st.table(st.session_state.temp_escala)
            if st.button("✅ Gravar na Planilha Google"):
                try:
                    sh = conectar_planilha()
                    aba = sh.worksheet("Escalas")
                    for r in st.session_state.temp_escala.values.tolist():
                        aba.append_row(r)
                    st.success("Gravado com sucesso!")
                    del st.session_state.temp_escala
                except: st.error("Erro ao salvar.")

        # BOTÃO DE LIMPEZA
        st.divider()
        if st.button("🗑️ Limpar Mês Anterior (Aba Escalas)"):
            try:
                sh = conectar_planilha()
                aba = sh.worksheet("Escalas")
                dados = aba.get_all_records()
                if dados:
                    df_l = pd.DataFrame(dados)
                    df_l['dt'] = pd.to_datetime(df_l['Data'], dayfirst=True, errors='coerce')
                    mes_ant = (hoje_br.replace(day=1) - timedelta(days=1)).month
                    df_f = df_l[df_l['dt'].dt.month != mes_ant].drop(columns=['dt'])
                    aba.clear()
                    aba.update([df_f.columns.values.tolist()] + df_f.values.tolist())
                    st.success("Limpeza concluída!")
            except: st.error("Erro na limpeza.")

        if st.button("Sair do Painel"):
            st.session_state.admin_ok = False
            st.rerun()
    
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
