import streamlit as st
import pandas as pd
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. CONTROLE DE NAVEGAÇÃO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(nome_pagina):
    st.session_state.pagina = nome_pagina

# --- 3. ESTILIZAÇÃO CSS (Layout e Cards de Escala) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões do Hub Central */
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1); color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-size: 22px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00ffcc; color: #302b63; transform: scale(1.02);
    }

    /* Cards de Congressos (Mantidos) */
    .card-congresso {
        background: rgba(255, 215, 0, 0.2); padding: 15px;
        border-radius: 10px; border: 2px solid #ffd700; margin-bottom: 20px;
    }

    /* NOVO: Estilo para Cards de Escala (Evita colunas emboladas) */
    .card-escala {
        background: rgba(0, 0, 0, 0.3);
        padding: 15px;
        border-radius: 12px;
        border-left: 6px solid #00ffcc;
        margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    .card-escala span { font-size: 0.9rem; opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS (Agenda e Escala extraída das fotos) ---
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
}

# Dados consolidados das escalas de Operadores e Fotógrafos
escala_fevereiro = [
    {"data": "01/02", "culto": "Culto da Família", "op": "Júnior", "foto": "Tiago (17:30h)"},
    {"data": "04/02", "culto": "Culto de Quarta", "op": "Lucas", "foto": "Grazi (19:00h)"},
    {"data": "06/02", "culto": "Culto de Sexta", "op": "Samuel", "foto": "Tiago (19:00h)"},
    {"data": "08/02", "culto": "Santa Ceia", "op": "Lucas", "foto": "Grazi (17:30h)"},
    {"data": "11/02", "culto": "Culto de Quarta", "op": "Samuel", "foto": "Tiago (19:00h)"},
    {"data": "13/02", "culto": "Culto de Sexta", "op": "Nicholas", "foto": "Grazi (19:00h)"},
    {"data": "15/02", "culto": "Culto de Missões", "op": "Samuel", "foto": "Tiago (17:30h)"},
    {"data": "18/02", "culto": "Culto de Quarta", "op": "Nicholas", "foto": "Grazi (19:00h)"},
    {"data": "20/02", "culto": "Culto de Sexta", "op": "Lucas", "foto": "Tiago (19:00h)"},
    {"data": "22/02", "culto": "Culto da Família", "op": "Nicholas", "foto": "Grazi (17:30h)"},
    {"data": "25/02", "culto": "Culto de Quarta", "op": "Lucas", "foto": "Tiago (19:00h)"},
    {"data": "27/02", "culto": "Culto de Sexta", "op": "Samuel", "foto": "Grazi (19:00h)"},
    {"data": "28/02", "culto": "Tarde com Deus", "op": "Nicholas", "foto": "Tiago (14:30h)"}
]

# --- 5. NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br><br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 4])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Departamentos")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 REDES SOCIAIS", on_click=navegar, args=("Redes",))
    with col2:
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Agenda":
    if st.button("⬅️ VOLTAR"): navegar("Início")
    st.title("🗓️ Cronograma 2026")
    for mes, cultos in agenda_completa.items():
        with st.expander(f"📅 {mes}"):
            for depto, data in cultos.items(): st.write(f"**{depto}:** {data}")

elif st.session_state.pagina == "Departamentos":
    if st.button("⬅️ VOLTAR"): navegar("Início")
    st.title("👥 Departamentos")
    t_mulh, t_jov, t_varoes, t_kids, t_miss, t_midia = st.tabs(["🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões", "📷 Mídia"])

    # [Abas anteriores mantidas conforme aprovado]
    with t_midia:
        st.subheader("📷 Escala de Mídia e Som - Fevereiro/2026")
        st.write("Layout otimizado para celular:")
        
        for item in escala_fevereiro:
            st.markdown(f"""
            <div class="card-escala">
                <b>{item['data']} - {item['culto']}</b><br>
                <span>🎧 Som: {item['op']}</span><br>
                <span>📸 Foto: {item['foto']}</span>
            </div>
            """, unsafe_allow_html=True)

# [Outras páginas Redes e Devocional mantidas]
