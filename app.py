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
# --- 1. CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

# Fuso Horário e Datas
fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

# Memória de Navegação
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state:
    st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

# --- 2. CONEXÃO COM GOOGLE SHEETS ---
def conectar_planilha():
    # Aqui usa os segredos que você já configurou no Streamlit Cloud
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    return client.open("NOME_DA_SUA_PLANILHA") # <--- AJUSTE O NOME AQUI

def carregar_dados(aba_nome):
    try:
        sh = conectar_planilha()
        aba = sh.worksheet(aba_nome)
        dados = aba.get_all_records()
        return pd.DataFrame(dados)
    except:
        return pd.DataFrame()

# --- 3. ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, p, span { color: #FFFFFF !important; font-weight: 700 !important; }
    
    /* Quadro Amarelo (Aniversariantes e Escalas) */
    .card-destaque {
        background: rgba(255, 215, 0, 0.1) !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important; 
        padding: 15px !important;
        margin-bottom: 15px !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Botões do Menu */
    button[data-testid="stBaseButton-secondary"] {
        width: 100% !important; background-color: #0a3d62 !important; 
        border: 2px solid #3c6382 !important; border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =================================================================
# --- 4. ROTEADOR DE PÁGINAS (ESTRUTURA EM GAVETAS) ---
# =================================================================

# --- PÁGINA: INÍCIO ---
if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    # Quadro de Cultos
    st.markdown("""
        <div style="background: rgba(10, 61, 98, 0.4); border: 1px solid #3c6382; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
            <h4 style="margin:0; color:#ffd700; text-align:center;">🙏 Nossos Cultos</h4>
            <p style="text-align:center; margin:5px 0;">Quarta e Sexta: 19h30 | Domingo: 18h00</p>
        </div>
    """, unsafe_allow_html=True)

    # Menu de Botões
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="btn_age")
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",), key="btn_aniv")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="btn_gst")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="btn_esc")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), key="btn_med")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="btn_lei")

# --- PÁGINA: AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_age")
    st.markdown("<h1>🗓️ Agenda de Eventos</h1>", unsafe_allow_html=True)
    # Conteúdo da Agenda...

# --- PÁGINA: ESCALAS (O que os membros vêem) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_esc")
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt'] = pd.to_datetime(df_e['Data'], dayfirst=True, errors='coerce')
        prox = df_e[df_e['dt'].dt.date >= hoje_br].sort_values(by='dt')
        for _, r in prox.iterrows():
            st.markdown(f"""
                <div class="card-destaque">
                    <b style="color:#ffd700;">{r['Data']} - {r['Evento']}</b><br>
                    👤 {r['Responsável']} | 📍 {r['Departamento']}<br>
                    ⏰ Chegada: {r['Horário']}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma escala publicada.")

# --- PÁGINA: LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_lei")
    st.markdown("<h1>📜 Plano de Leitura Bíblica</h1>", unsafe_allow_html=True)
    st.write("Acompanhe aqui o seu progresso diário.")

# --- PÁGINA: GESTÃO (Onde a IA gera as escalas) ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v_gst")
    st.markdown("<h1>⚙️ Painel de Gestão</h1>", unsafe_allow_html=True)

    if not st.session_state.admin_ok:
        with st.form("login"):
            senha = st.text_input("Senha de Líder:", type="password")
            if st.form_submit_button("Acessar"):
                if senha == "ISOSED2026":
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta!")
    else:
        st.success("Bem-vindo, Líder!")
        col_m, col_a = st.columns(2)
        with col_m: mes_s = st.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        with col_a: ano_s = st.number_input("Ano:", value=2026)

        t_rec, t_foto, t_ops = st.tabs(["🤝 Recepção", "📸 Fotógrafos", "🔊 Operadores"])

        import calendar
        cal = calendar.Calendar()
        dias = [d for sem in cal.monthdatescalendar(ano_s, mes_s) for d in sem if d.month == mes_s]
        u_sab = max([d for d in dias if d.weekday() == 5])
        datas_alvo = [d for d in dias if d.weekday() in [2, 4, 6] or d == u_sab]
        datas_alvo.sort()

        with t_rec:
            if st.button("🤖 Gerar Recepção"):
                eq = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                res, idx = [], 0
                for d in datas_alvo:
                    p1, p2 = eq[idx % 7], eq[(idx + 1) % 7]
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Recepção", "Responsável": f"{p1} e {p2}"})
                    idx += 2
                st.session_state.temp_escala = pd.DataFrame(res)

        with t_foto:
            if st.button("🤖 Gerar Fotógrafos"):
                eq = ["Tiago", "Grazi"]
                res = []
                for i, d in enumerate(datas_alvo):
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Fotografia", "Responsável": eq[i % 2]})
                st.session_state.temp_escala = pd.DataFrame(res)

        with t_ops:
            if st.button("🤖 Gerar Operadores"):
                p_g, p_d = ["Lucas", "Samuel", "Nicholas"], ["Júnior", "Lucas", "Samuel", "Nicholas"]
                res, ig, idom = [], 0, 0
                for d in datas_alvo:
                    op = p_d[idom % 4] if d.weekday()==6 else p_g[ig % 3]
                    if d.weekday()==6: idom += 1
                    else: ig += 1
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Mídia", "Responsável": op})
                st.session_state.temp_escala = pd.DataFrame(res)

        if "temp_escala" in st.session_state:
            st.divider()
            st.dataframe(st.session_state.temp_escala, use_container_width=True)
            if st.button("✅ Gravar na Planilha"):
                sh = conectar_planilha()
                aba = sh.worksheet("Escalas")
                for r in st.session_state.temp_escala.values.tolist():
                    aba.append_row(r)
                st.success("Salvo com sucesso!")
                del st.session_state.temp_escala

        st.divider()
        if st.button("🗑️ Limpar Mês Anterior"):
            # Lógica de limpeza da planilha aqui...
            pass

        if st.button("Sair"):
            st.session_state.admin_ok = False
            st.rerun()
