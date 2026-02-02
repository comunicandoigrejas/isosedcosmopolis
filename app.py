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

# --- 3. ESTILIZAÇÃO CSS (Clean App, Hub e Cards) ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos do Streamlit */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões Padronizados (Hub e Voltar) */
    div.stButton > button {
        width: 100%; height: 120px; border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1); color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-size: 22px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00ffcc; color: #302b63; transform: scale(1.02);
    }
    
    /* Botão Voltar (Ajuste de altura menor para não ocupar muito espaço) */
    .btn-voltar div.stButton > button {
        height: 60px;
        font-size: 18px;
        margin-bottom: 20px;
    }

    /* Cards e Itens de Agenda */
    .card-congresso {
        background: rgba(255, 215, 0, 0.2); padding: 15px;
        border-radius: 10px; border: 2px solid #ffd700; margin-bottom: 20px;
    }
    .data-item {
        background: rgba(0, 0, 0, 0.3); padding: 8px 15px;
        border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #00ffcc;
    }
    .card-escala {
        background: rgba(0, 0, 0, 0.3); padding: 15px;
        border-radius: 12px; border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS MANTIDOS ---
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
}

escala_midia_dados = [
    {"data": "01/02", "culto": "Família", "op": "Júnior", "foto": "Tiago (17:30)"},
    {"data": "04/02", "culto": "Quarta", "op": "Lucas", "foto": "Grazi (19:00)"},
    {"data": "06/02", "culto": "Sexta", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "08/02", "culto": "Santa Ceia", "op": "Lucas", "foto": "Grazi (17:30)"},
    {"data": "11/02", "culto": "Quarta", "op": "Samuel", "foto": "Tiago (19:00)"},
    {"data": "13/02", "culto": "Sexta", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "15/02", "culto": "Missões", "op": "Samuel", "foto": "Tiago (17:30)"},
    {"data": "18/02", "culto": "Quarta", "op": "Nicholas", "foto": "Grazi (19:00)"},
    {"data": "20/02", "culto": "Sexta", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "22/02", "culto": "Família", "op": "Nicholas", "foto": "Grazi (17:30)"},
    {"data": "25/02", "culto": "Quarta", "op": "Lucas", "foto": "Tiago (19:00)"},
    {"data": "27/02", "culto": "Sexta", "op": "Samuel", "foto": "Grazi (19:00)"},
    {"data": "28/02", "culto": "Tarde com Deus", "op": "Nicholas", "foto": "Tiago (14:30)"}
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
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("🗓️ Cronograma Geral 2026")
    for mes, cultos in agenda_completa.items():
        with st.expander(f"📅 {mes}"):
            for depto, data in cultos.items(): st.write(f"**{depto}:** {data}")

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)

    st.title("👥 Departamentos e Escalas")
    t_mulh, t_jov, t_varoes, t_kids, t_miss, t_midia = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões", "📷 Mídia"
    ])
    
    with t_mulh:
        st.markdown('<div class="card-congresso">🌟 <b>CONGRESSOS:</b><br>08/03: Evento Especial (Manhã)<br>17/10: Outubro Rosa (Noite)<br>21/11: Conferência com a Bispa</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Irmãs" in cultos: st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Irmãs"]}</div>', unsafe_allow_html=True)
    with t_jov:
        st.markdown('<div class="card-congresso">🌟 <b>CONGRESSOS:</b><br>14 a 17/02: Retiro de Jovens<br>05 e 06/06: Congresso de Jovens</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Jovens" in cultos: st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Jovens"]}</div>', unsafe_allow_html=True)
    with t_varoes:
        st.markdown('<div class="card-congresso">🌟 <b>CONGRESSO:</b><br>24 e 25/04: Congresso de Varões</div>', unsafe_allow_html=True)
        for mes, cultos in agenda_completa.items():
            if "Varões" in cultos: st.markdown(f'<div class="data-item"><b>{mes}:</b> {cultos["Varões"]}</div>', unsafe_allow_html=True)
    with t_kids:
        st.markdown('<div class="card-congresso">🌟 <b>CONGRESSO:</b><br>30 e 31/10: Congresso de Crianças</div>', unsafe_allow_html=True)
    with t_miss:
        st.markdown('<div class="card-congresso">🌟 <b>CONGRESSO:</b><br>14 e 15/08: Congresso de Missões<br>Todo 3º Domingo: Culto de Missões</div>', unsafe_allow_html=True)
    with t_midia:
        st.subheader("📷 Escala de Fevereiro/2026")
        for item in escala_midia_dados:
            st.markdown(f"""
            <div class="card-escala">
                <b>{item['data']} - {item['culto']}</b><br>
                <span>🎧 Som: {item['op']} | 📸 Foto: {item['foto']}</span>
            </div>
            """, unsafe_allow_html=True)

elif st.session_state.pagina == "Redes":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia ISOSED")

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Devocional")
