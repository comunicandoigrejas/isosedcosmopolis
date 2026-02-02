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
    
    .btn-voltar div.stButton > button {
        height: 60px; font-size: 18px; margin-bottom: 20px;
    }

    /* Estilos de Cards e Itens */
    .card-congresso {
        background: rgba(255, 215, 0, 0.2); padding: 15px;
        border-radius: 10px; border: 2px solid #ffd700; margin-bottom: 20px;
    }
    .data-item {
        background: rgba(0, 0, 0, 0.3); padding: 8px 15px;
        border-radius: 5px; margin-bottom: 5px; border-left: 4px solid #00ffcc;
    }
    .card-escala {
        background: rgba(0, 0, 0, 0.3); padding: 15px;
        border-radius: 12px; border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BANCO DE DADOS DA AGENDA 2026 ---
agenda_completa_2026 = {
    "Janeiro": [
        "16/01 (Sex) – 🧑‍🎓 Jovens", "18/01 (Dom) – 🌍 Culto de Missões",
        "23/01 (Sex) – 👔 Varões", "30/01 (Sex) – 🎤 Louvor", "31/01 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Fevereiro": [
        "06/02 (Sex) – 👗 Irmãs", "13/02 (Sex) – 🧑‍🎓 Jovens", "14 a 17/02 – 🚌 Retiro de Jovens",
        "15/02 (Dom) – 🌍 Culto de Missões", "20/02 (Sex) – 👔 Varões", "27/02 (Sex) – 🎤 Louvor", "28/02 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Março": [
        "06/03 (Sex) – 👗 Irmãs", "08/03 (Dom) – 🌸 Evento Mulheres (Manhã)", "13/03 (Sex) – 🧑‍🎓 Jovens",
        "15/03 (Dom) – 🌍 Culto de Missões", "20/03 (Sex) – 👔 Varões", "27/03 (Sex) – 🎤 Louvor", "28/03 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Abril": [
        "03/04 (Sex) – 👗 Irmãs", "10/04 (Sex) – 🧑‍🎓 Jovens", "17/04 (Sex) – 👔 Varões", "19/04 (Dom) – 🌍 Culto de Missões",
        "24/04 (Sex) – 🎤 Louvor", "24 e 25/04 – 🛡️ Congresso de Varões", "25/04 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Maio": [
        "01/05 (Sex) – 👗 Irmãs", "08/05 (Sex) – 🧑‍🎓 Jovens", "15/05 (Sex) – 👔 Varões", "17/05 (Dom) – 🌍 Culto de Missões",
        "22/05 (Sex) – 🎤 Louvor", "29/05 (Sex) – 👗 Irmãs (5ª Sexta)", "30/05 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Junho": [
        "05/06 (Sex) – 🧑‍🎓 Jovens", "05 e 06/06 – 🔥 Congresso de Jovens", "12/06 (Sex) – 👔 Varões",
        "19/06 (Sex) – 🎤 Louvor", "21/06 (Dom) – 🌍 Culto de Missões", "26/06 (Sex) – 👗 Irmãs", "27/06 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Julho": [
        "03/07 (Sex) – 🧑‍🎓 Jovens", "10/07 (Sex) – 👔 Varões", "17/07 (Sex) – 🎤 Louvor", "19/07 (Dom) – 🌍 Culto de Missões",
        "24/07 (Sex) – 👗 Irmãs", "25/07 (Sáb) – 🙏 Tarde com Deus", "31/07 (Sex) – 🧑‍🎓 Jovens (5ª Sexta)"
    ],
    "Agosto": [
        "07/08 (Sex) – 👔 Varões", "14/08 (Sex) – 🎤 Louvor", "14 e 15/08 – 🌍 Congresso de Missões",
        "16/08 (Dom) – 🌍 Culto de Missões", "21/08 (Sex) – 👗 Irmãs", "28/08 (Sex) – 🧑‍🎓 Jovens", "29/08 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Setembro": [
        "04/09 (Sex) – 👔 Varões", "11/09 (Sex) – 🎤 Louvor", "18/09 (Sex) – 👗 Irmãs", "20/09 (Dom) – 🌍 Culto de Missões",
        "25/09 (Sex) – 🧑‍🎓 Jovens", "26/09 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Outubro": [
        "02/10 (Sex) – 👔 Varões", "09/10 (Sex) – 🎤 Louvor", "16/10 (Sex) – 👗 Irmãs", "17/10 (Sáb) – 💗 Outubro Rosa (Noite)",
        "18/10 (Dom) – 🌍 Culto de Missões", "23/10 (Sex) – 🧑‍🎓 Jovens", "30/10 (Sex) – 👔 Varões (5ª Sexta)",
        "30 e 31/10 – 🎈 Congresso Kids", "31/10 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Novembro": [
        "06/11 (Sex) – 🎤 Louvor", "13/11 (Sex) – 👗 Irmãs", "15/11 (Dom) – 🌍 Culto de Missões",
        "20/11 (Sex) – 🧑‍🎓 Jovens", "21/11 (Sáb) – 👑 Conf. Mulheres (Bispa)", "27/11 (Sex) – 👔 Varões", "28/11 (Sáb) – 🙏 Tarde com Deus"
    ],
    "Dezembro": [
        "04/12 (Sex) – 🎤 Louvor", "11/12 (Sex) – 👗 Irmãs", "18/12 (Sex) – 🧑‍🎓 Jovens",
        "20/12 (Dom) – 🌍 Culto de Missões", "25/12 (Sex) – ❌ Sem Culto (Natal)", "27/12 (Dom) – 🙏 Tarde com Deus"
    ]
}

# Dados de Mídia extraídos das imagens
escala_midia_fevereiro = [
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

# --- 5. NAVEGAÇÃO E PÁGINAS ---

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
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🕒 Domingos 18h | Quartas 19h30 | Sextas 19h30")

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.title("🗓️ Cronograma Completo 2026")
    for mes, eventos in agenda_completa_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in eventos: st.write(f"• {ev}")

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)

    st.title("👥 Departamentos e Escalas")
    t_mulh, t_jov, t_varoes, t_kids, t_miss, t_midia = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões", "📷 Mídia"
    ])
    
    with t_mulh:
        st.markdown('<div class="card-congresso">🌟 <b>EVENTOS:</b><br>08/03: Evento Especial (Manhã)<br>17/10: Outubro Rosa (Noite)<br>21/11: Conferência com a Bispa</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, evs in agenda_completa_2026.items():
            for ev in evs:
                if "Irmãs" in ev: st.markdown(f'<div class="data-item"><b>{mes}:</b> {ev}</div>', unsafe_allow_html=True)

    with t_jov:
        st.markdown('<div class="card-congresso">🌟 <b>EVENTOS:</b><br>14 a 17/02: Retiro de Jovens<br>05 e 06/06: Congresso de Jovens</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, evs in agenda_completa_2026.items():
            for ev in evs:
                if "Jovens" in ev: st.markdown(f'<div class="data-item"><b>{mes}:</b> {ev}</div>', unsafe_allow_html=True)

    with t_varoes:
        st.markdown('<div class="card-congresso">🌟 <b>EVENTO:</b><br>24 e 25/04: Congresso de Varões</div>', unsafe_allow_html=True)
        st.subheader("📅 Cultos de Sexta-feira")
        for mes, evs in agenda_completa_2026.items():
            for ev in evs:
                if "Varões" in ev: st.markdown(f'<div class="data-item"><b>{mes}:</b> {ev}</div>', unsafe_allow_html=True)

    with t_kids:
        st.markdown('<div class="card-congresso">🌟 <b>EVENTO:</b><br>30 e 31/10: Congresso Kids</div>', unsafe_allow_html=True)
        st.write("🎈 Atividades todos os domingos às 18h.")

    with t_miss:
        st.markdown('<div class="card-congresso">🌟 <b>EVENTO:</b><br>14 e 15/08: Congresso de Missões</div>', unsafe_allow_html=True)
        st.subheader("🌍 Cultos de Missões (Todo 3º Domingo)")
        for mes, evs in agenda_completa_2026.items():
            for ev in evs:
                if "Missões" in ev: st.markdown(f'<div class="data-item"><b>{mes}:</b> {ev}</div>', unsafe_allow_html=True)

    with t_midia:
        st.subheader("📷 Escala de Fevereiro/2026")
        for item in escala_midia_fevereiro:
            st.markdown(f"""
            <div class="card-escala">
                <b>{item['data']} - {item['culto']}</b><br>
                <span>🎧 Som: {item['op']} | 📸 Foto: {item['foto']}</span>
            </div>
            """, unsafe_allow_html=True)

# Outras seções (Redes e Devocional) mantidas conforme padrão
elif st.session_state.pagina == "Redes":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia ISOSED")

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Espaço Devocional")
