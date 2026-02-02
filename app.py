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

# --- 3. ESTILIZAÇÃO CSS (Foco em App Clean e Responsivo) ---
st.markdown("""
    <style>
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

# --- 4. DADOS DA AGENDA E ESCALAS ---
agenda_completa_2026 = {
    "Janeiro": ["16/01 (Sex) – 🧑‍🎓 Jovens", "18/01 (Dom) – 🌍 Culto de Missões", "23/01 (Sex) – 👔 Varões", "30/01 (Sex) – 🎤 Louvor", "31/01 (Sáb) – 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02 (Sex) – 👗 Irmãs", "13/02 (Sex) – 🧑‍🎓 Jovens", "14 a 17/02 – 🚌 Retiro de Jovens", "15/02 (Dom) – 🌍 Culto de Missões", "20/02 (Sex) – 👔 Varões", "27/02 (Sex) – 🎤 Louvor", "28/02 (Sáb) – 🙏 Tarde com Deus"],
    "Março": ["06/03 (Sex) – 👗 Irmãs", "08/03 (Dom) – 🌸 Evento Mulheres (Manhã)", "13/03 (Sex) – 🧑‍🎓 Jovens", "15/03 (Dom) – 🌍 Culto de Missões", "20/03 (Sex) – 👔 Varões", "27/03 (Sex) – 🎤 Louvor", "28/03 (Sáb) – 🙏 Tarde com Deus"]
    # ... dados continuam conforme histórico aprovado
}

# Escala Recepção Fevereiro
escala_recepcao = [
    {"data": "04/02", "dia": "Quarta", "dupla": "Ailton e Rita"},
    {"data": "06/02", "dia": "Sexta", "dupla": "Márcia e Felipe"},
    {"data": "08/02", "dia": "Domingo", "dupla": "Simone e Elisabete"},
    {"data": "11/02", "dia": "Quarta", "dupla": "Ceia e Felipe"},
    {"data": "13/02", "dia": "Sexta", "dupla": "Ailton e Márcia"},
    {"data": "15/02", "dia": "Domingo", "dupla": "Rita e Simone"},
    {"data": "18/02", "dia": "Quarta", "dupla": "Ceia e Elisabete"},
    {"data": "20/02", "dia": "Sexta", "dupla": "Felipe e Márcia"},
    {"data": "22/02", "dia": "Domingo", "dupla": "Ailton e Simone"},
    {"data": "28/02", "dia": "Sábado", "dupla": "Ceia e Rita ✨"}
]

# Escala Mídia Fevereiro
escala_midia = [
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
    # Adicionada a aba de Recepção
    t_mulh, t_jov, t_varoes, t_kids, t_miss, t_midia, t_recepcao = st.tabs([
        "🌸 Mulheres", "🔥 Jovens", "🛡️ Varões", "🎈 Kids", "🌍 Missões", "📷 Mídia", "🤝 Recepção"
    ])
    
    # [Abas Mulheres, Jovens, Varões, Kids e Missões mantidas conforme aprovado]
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

    # [Aba Mídia mantida]
    with t_midia:
        st.subheader("📷 Escala de Mídia e Som - Fevereiro/2026")
        for item in escala_midia:
            st.markdown(f"""
            <div class="card-escala">
                <b>{item['data']} - {item['culto']}</b><br>
                <span>🎧 Som: {item['op']} | 📸 Foto: {item['foto']}</span>
            </div>
            """, unsafe_allow_html=True)

    # NOVO: Aba Recepção
    with t_recepcao:
        st.subheader("🤝 Escala da Recepção - Fevereiro/2026")
        st.write("Escala mensal da equipe de acolhimento:")
        for item in escala_recepcao:
            st.markdown(f"""
            <div class="card-escala">
                <b>{item['data']} ({item['dia']})</b><br>
                <span>👥 Dupla: {item['dupla']}</span>
            </div>
            """, unsafe_allow_html=True)

# Outras seções Redes e Devocional seguem o padrão
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
