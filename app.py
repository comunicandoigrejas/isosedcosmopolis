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

# --- 1. CONFIGURAÇÕES E MEMÓRIA ---
st.set_page_config(page_title="ISOSED Cosmópolis", layout="wide", page_icon="⛪")

fuso_br = pytz.timezone('America/Sao_Paulo')
hoje_br = datetime.now(fuso_br).date()

if 'pagina' not in st.session_state: st.session_state.pagina = "Início"
if 'admin_ok' not in st.session_state: st.session_state.admin_ok = False

def navegar(p):
    st.session_state.pagina = p

# --- 2. CONEXÃO COM O GOOGLE SHEETS ---
def conectar_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # TROQUE ABAIXO PELO NOME QUE APARECE LÁ NO TOPO DA SUA PLANILHA
        nome_real = "COLOQUE_AQUI_O_NOME_DA_SUA_PLANILHA" 
        
        return client.open(nome_real)
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("❌ Erro: O Google não encontrou nenhuma planilha com esse nome. Verifique se o nome está idêntico.")
        return None
    except Exception as e:
        st.error(f"❌ Erro de Permissão ou Conexão: {e}")
        return None
# --- 3. ESTILO VISUAL (CSS) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }
    h1, h2, h3, h4, h5, h6, p, span { color: #FFFFFF !important; font-weight: 700 !important; }
    .card-isosed {
        background: rgba(255, 215, 0, 0.1) !important; 
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important; padding: 15px !important; margin-bottom: 15px !important;
    }
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
    
    st.markdown("""
        <div style="background: rgba(10, 61, 98, 0.4); border: 1px solid #3c6382; border-radius: 10px; padding: 15px; margin-bottom: 20px; text-align: center;">
            <h4 style="margin:0; color:#ffd700;">🙏 Nossos Cultos</h4>
            <p style="margin:5px 0;">Segunda: Oração | Quarta e Sexta: 19h30 | Domingo: 18h00</p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), key="b1")
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",), key="b2")
        st.button("⚙️ Painel do Líder", on_click=navegar, args=("Gestao",), key="b3")
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), key="b4")
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), key="b5")
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), key="b6")

    # --- RODAPÉ: LOGO, REDES E CONTADOR ---
    st.markdown("<br><hr style='opacity:0.2;'>", unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 2, 1])
    with f2:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", use_container_width=True)
        st.markdown("""
            <div style="text-align: center; margin: 15px 0;">
                <a href="#" style="text-decoration:none; color:#ffd700; margin:0 10px;">📸 Instagram</a>
                <a href="#" style="text-decoration:none; color:#ffd700; margin:0 10px;">🎥 YouTube</a>
            </div>
        """, unsafe_allow_html=True)
        if 'visitas' not in st.session_state: st.session_state.visitas = atualizar_contador()
        st.markdown(f"<p style='text-align:center; opacity:0.5; font-size:0.8em;'>Visitante nº: {st.session_state.visitas}</p>", unsafe_allow_html=True)

# --- PÁGINA: AGENDA ---
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v1")
    st.markdown("<h1>🗓️ Agenda de Eventos</h1>", unsafe_allow_html=True)
    # Conteúdo da agenda aqui...

# --- PÁGINA: ESCALAS (Visão Membros) ---
elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v2")
    st.markdown("<h1>📢 Escalas Publicadas</h1>", unsafe_allow_html=True)
    df_e = carregar_dados("Escalas")
    if not df_e.empty:
        df_e['dt'] = pd.to_datetime(df_e['Data'], dayfirst=True, errors='coerce')
        for _, r in df_e[df_e['dt'].dt.date >= hoje_br].sort_values('dt').iterrows():
            st.markdown(f'<div class="card-isosed"><b style="color:#ffd700;">{r["Data"]} - {r["Evento"]}</b><br>'
                        f'👤 {r["Responsável"]} | 📍 {r["Departamento"]} | ⏰ {r["Horário"]}</div>', unsafe_allow_html=True)
    else: st.info("Nenhuma escala disponível.")

# --- PÁGINA: LEITURA ---
elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v3")
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)
    st.write("Acompanhe o plano de leitura bíblica anual.")

# --- PÁGINA: GESTÃO (Painel do Líder) ---
elif st.session_state.pagina == "Gestao":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="v4")
    if not st.session_state.admin_ok:
        with st.form("login"):
            senha = st.text_input("Senha de Líder:", type="password")
            if st.form_submit_button("Entrar"):
                if senha == "ISOSED2026": 
                    st.session_state.admin_ok = True
                    st.rerun()
                else: st.error("Senha incorreta!")
    else:
        st.success("Painel de Controle Ativo")
        m_col, a_col = st.columns(2)
        mes_s = m_col.selectbox("Mês:", list(range(1,13)), index=hoje_br.month-1)
        ano_s = a_col.number_input("Ano:", value=2026)

        t1, t2, t3 = st.tabs(["🤝 Recepção", "📸 Fotógrafos", "🔊 Som"])
        
        import calendar
        cal = calendar.Calendar()
        dias = [d for sem in cal.monthdatescalendar(ano_s, mes_s) for d in sem if d.month == mes_s]
        u_sab = max([d for d in dias if d.weekday() == 5])
        datas_alvo = sorted([d for d in dias if d.weekday() in [2, 4, 6] or d == u_sab])

        with t1:
            if st.button("🤖 Gerar Recepção"):
                eq = ["Ailton", "Márcia", "Simone", "Ceia", "Elisabete", "Felipe", "Rita"]
                res, idx = [], 0
                for d in datas_alvo:
                    p1, p2 = eq[idx % 7], eq[(idx + 1) % 7]
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Recepção", "Responsável": f"{p1} e {p2}"})
                    idx += 2
                st.session_state.temp_escala = pd.DataFrame(res)

        with t2:
            if st.button("🤖 Gerar Fotógrafos"):
                eq = ["Tiago", "Grazi"]
                res = []
                for i, d in enumerate(datas_alvo):
                    h = "14h30" if d == u_sab else ("17h30" if d.weekday()==6 else "19h00")
                    res.append({"Data": d.strftime('%d/%m/%Y'), "Dia": d.strftime('%A'), "Horário": h, "Evento": "Culto", "Departamento": "Fotografia", "Responsável": eq[i % 2]})
                st.session_state.temp_escala = pd.DataFrame(res)

        with t3:
            if st.button("🤖 Gerar Som"):
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
            st.dataframe(st.session_state.temp_escala, use_container_width=True)
            if st.button("✅ Gravar na Planilha"):
                sh = conectar_planilha()
                if sh:
                    aba = sh.worksheet("Escalas")
                    for r in st.session_state.temp_escala.values.tolist(): aba.append_row(r)
                    st.success("Salvo!")
                    del st.session_state.temp_escala

        if st.button("Sair"):
            st.session_state.admin_ok = False
            st.rerun()
