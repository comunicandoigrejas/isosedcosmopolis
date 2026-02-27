import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import gspread
from google.oauth2.service_account import Credentials
import os
import calendar

# =========================================================
# 1. CONFIGURAÇÕES, DATAS E MEMÓRIA
# =========================================================
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

# Sistema de Navegação
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state:
    st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

# =========================================================
# 2. CONEXÃO MESTRA COM O GOOGLE SHEETS
# =========================================================
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # --- AQUI ESTÁ O SEGREDO: COLE O ID CORRETO ABAIXO ---
        # Ex: 1BxiMVs0XRA5nSMfB6Y6n6vCCvN-01A2B3C4D5E6F7G8H
        ID_DA_PLANILHA = "COLE_O_ID_AQUI" 
        
        return client.open_by_key(ID_DA_PLANILHA)
    except Exception as e:
        st.error(f"Erro Crítico de Conexão: {e}")
        return None

def carregar_dados(aba_nome):
    sh = conectar_planilha()
    if sh:
        try:
            aba = sh.worksheet(aba_nome)
            return pd.DataFrame(aba.get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

def atualizar_contador():
    try:
        sh = conectar_planilha()
        aba = sh.worksheet("Acessos")
        valor = int(aba.acell('A2').value or 0) + 1
        aba.update_acell('A2', valor)
        return valor
    except: return "---"

# --- ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1a1a2e !important; }
    .card-isosed {
        background: rgba(255, 215, 0, 0.1) !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 15px; padding: 15px; margin-bottom: 12px;
    }
    .stButton>button {
        width: 100% !important; background-color: #0f3460 !important; 
        color: white !important; border-radius: 10px !important;
        font-weight: bold; border: 1px solid #16213e; height: 3.5em;
    }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 3. ROTEADOR DE PÁGINAS (ALINHAMENTO BLINDADO)
# =========================================================

# --- GAVETA 1: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h1>ISOSED COSMÓPOLIS</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border-bottom: 4px solid #ffd700; text-align: center;">
            <p style="margin:0; font-size: 1.2em;"><b>"Só o Senhor é Deus"</b></p>
            <p style="opacity: 0.8;">Quarta e Sexta: 19h30 | Domingo: 18h00</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="m1")
        st.button("🎂 Aniversários", on_click=navegar, args=("Aniv",), key="m2")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="m3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="m4")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), key="m5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="m6")

    # --- RODAPÉ: LOGO, REDES E CONTADOR ---
    st.markdown("<br><hr style='opacity:0.1;'>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 2, 1])
    with f2:
        if os.path.exists("logo igreja.png"): 
            st.image("logo igreja.png", use_container_width=True)
        
        st.markdown("""
            <div style="text-align: center; margin: 15px 0;">
                <a href="https://instagram.com/isosedcosmopolis" style="color:#ffd700; text-decoration:none; margin:0 15px;">📸 Instagram</a>
                <a href="https://youtube.com/@isosedcosmopolis" style="color:#ffd700; text-decoration:none; margin:0 15px;">🎥 YouTube</a>
            </div>
        """, unsafe_allow_html=True)
        
        if 'visitas' not in st.session_state:
            st.session_state.visitas = atualizar_contador()
        st.markdown(f"<p style='text-align:center; opacity:0.4; font-size:0.7em;'>Visitante nº: {st.session_state.visitas}</p>", unsafe_allow_html=True)

# --- GAVETA 2: AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_ag")
    st.markdown("<h2>🗓️ Agenda de Eventos</h2>", unsafe_allow_html=True)
    df_ag = carregar_dados("Agenda")
    if not df_ag.empty:
        st.dataframe(df_ag, use_container_width=True)
    else: st.info("Nenhum evento cadastrado para 2026.")

# --- GAVETA 3: ESCALAS (Visão Membros) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_esc")
    st.markdown("<h2>📢 Escalas de Serviço</h2>", unsafe_allow_html=True)
    
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt_obj'] = pd.to_datetime(df_e['Data'], dayfirst=True, errors='coerce')
        df_f = df_e[df_e['dt_obj'].dt.date >= hoje_br].sort_values('dt_obj')
        
        for _, r in df_f.iterrows():
            st.markdown(f"""
                <div class="card-isosed">
                    <b style="color:#ffd700;">{r['Data']} - {r['Dia']}</b><br>
                    <span style="font-size: 1.1em;">{r['Evento']}</span><br>
                    👤 <b>{r['Responsável']}</b> | 📍 {r['Departamento']}<br>
                    ⏰ Horário: {r['Horário']}
                </div>
            """, unsafe_allow_html=True)
    else: st.warning("As escalas ainda não foram publicadas pelo líder.")

# --- GAVETA 4: LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_lei")
    st.markdown("<h2>📜 Plano de Leitura Bíblica</h2>", unsafe_allow_html=True)
    st.info("Acompanhe o cronograma de leitura anual da ISOSED.")

# --- GAVETA 5: GESTÃO (Painel Restrito) ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_gs")
    st.markdown("<h2>⚙️ Gestão de Escalas ISOSED</h2>", unsafe_allow_html=True)

    if not st.session_state.admin_ok:
        with st.form("login_lider"):
            senha = st.text_input("Senha de Acesso:", type="password")
            if st.form_submit_button("Acessar Painel"):
                if senha == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta!")
    else:
        st.success("Acesso Autorizado!")
        c_m, c_a = st.columns(2)
        mes_gerar = c_m.selectbox("Mês:", list(range(1, 13)), index=hoje_br.month - 1)
        ano_gerar = c_a.number_input("Ano:", value=2026)

        tab_rec, tab_foto, tab_som = st.tabs(["🤝 Recepção", "📸 Fotografia", "🔊 Som/Mídia"])

        # Lógica de Datas
        cal = calendar.Calendar()
        dias_mes = [d for sem in cal.monthdatescalendar(ano_gerar, mes_gerar) for d in sem if d.month == mes_gerar]
        u_sab = max([d for d in dias_mes if d.weekday() == 5])
        datas_alvo = sorted([d for d in dias_mes if d.weekday() in [2, 4, 6] or d == u_sab])

        with tab_rec:
            if st.button("🤖 Gerar: Recepção"):
                eq = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                res, idx = [], 0
                for d in datas_alvo:
                    p1, p2 = eq[idx % 7], eq[(idx + 1) % 7]
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Recepção", "Responsável": f"{p1} e {p2}"})
                    idx += 2
                st.session_state.temp_escala = pd.DataFrame(res)

        with tab_foto:
            if st.button("🤖 Gerar: Fotografia"):
                eq = ["Tiago", "Grazi"]
                res = []
                for i, d in enumerate(datas_alvo):
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Fotografia", "Responsável": eq[i % 2]})
                st.session_state.temp_escala = pd.DataFrame(res)

        with tab_som:
            if st.button("🤖 Gerar: Som"):
                pg, pdm = ["Lucas", "Samuel", "Nicholas"], ["Júnior", "Lucas", "Samuel", "Nicholas"]
                res, ig, idm = [], 0, 0
                for d in datas_alvo:
                    op = pdm[idm % 4] if d.weekday()==6 else pg[ig % 3]
                    if d.weekday()==6: idm += 1
                    else: ig += 1
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Mídia", "Responsável": op})
                st.session_state.temp_escala = pd.DataFrame(res)

        if "temp_escala" in st.session_state:
            st.divider()
            st.dataframe(st.session_state.temp_escala, use_container_width=True)
            if st.button("✅ Gravar na Planilha Oficial"):
                try:
                    sh = conectar_planilha()
                    aba = sh.worksheet("Escalas")
                    for r in st.session_state.temp_escala.values.tolist():
                        aba.append_row(r)
                    st.success("Escala gravada com sucesso!")
                    del st.session_state.temp_escala
                except: st.error("Erro ao gravar. Verifique se a aba 'Escalas' existe.")

        if st.button("Sair do Painel"):
            st.session_state.admin_ok = False
            st.rerun()

# --- FIM DO ARQUIVO ---
