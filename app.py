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

# --- 3. ESTILIZAÇÃO CSS (Simetria Total e Design Pill) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stHeader"] {visibility: hidden;}
    [data-testid="stSidebar"] { display: none; }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d3436 100%);
        color: white;
    }
    
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões Pill Sincronizados (Largura e Altura Fixas) */
    div.stButton > button {
        width: 100% !important;
        height: 80px !important;
        border-radius: 40px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.3) !important;
        transition: 0.3s !important;
        text-transform: uppercase !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-bottom: 15px !important;
    }
    
    div.stButton:nth-of-type(1) > button { background-color: #0984e3 !important; } 
    div.stButton:nth-of-type(2) > button { background-color: #e17055 !important; }
    div.stButton:nth-of-type(3) > button { background-color: #00b894 !important; }
    div.stButton:nth-of-type(4) > button { background-color: #6c5ce7 !important; }

    div.stButton > button:hover {
        transform: scale(1.02) !important;
        filter: brightness(1.1) !important;
    }
    
    .btn-voltar div.stButton > button {
        background-color: rgba(255,255,255,0.1) !important;
        height: 50px !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        font-size: 14px !important;
    }

    .card-escala {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px; border-radius: 20px;
        border-left: 6px solid #00ffcc; margin-bottom: 12px;
    }
    .card-escala b { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. BANCO DE DADOS INTEGRAL 2026 ---
# Restaurado rigorosamente com base nas datas enviadas
agenda_2026 = {
    "Janeiro": ["16/01: 🧑‍🎓 Jovens", "18/01: 🌍 Missões", "23/01: 👔 Varões", "30/01: 🎤 Louvor", "31/01: 🙏 Tarde com Deus"],
    "Fevereiro": ["06/02: 👗 Irmãs", "13/02: 🧑‍🎓 Jovens", "14 a 17/02: 🚌 Retiro", "15/02: 🌍 Missões", "20/02: 👔 Varões", "27/02: 🎤 Louvor", "28/02: 🙏 Tarde com Deus"],
    "Março": ["06/03: 👗 Irmãs", "08/03: 🌸 Evento Mulheres", "13/03: 🧑‍🎓 Jovens", "15/03: 🌍 Missões", "20/03: 👔 Varões", "27/03: 🎤 Louvor", "28/03: 🙏 Tarde com Deus"],
    "Abril": ["03/04: 👗 Irmãs", "10/04: 🧑‍🎓 Jovens", "17/04: 👔 Varões", "19/04: 🌍 Missões", "24/04: 🎤 Louvor", "24 e 25/04: 🛡️ Congresso Varões", "25/04: 🙏 Tarde com Deus"],
    "Maio": ["01/05: 👗 Irmãs", "08/05: 🧑‍🎓 Jovens", "15/05: 👔 Varões", "17/05: 🌍 Missões", "22/05: 🎤 Louvor", "29/05: 👗 Irmãs (5ª Sex)", "30/05: 🙏 Tarde com Deus"],
    "Junho": ["05/06: 🧑‍🎓 Jovens", "05 e 06/06: 🔥 Congresso Jovens", "12/06: 👔 Varões", "19/06: 🎤 Louvor", "21/06: 🌍 Missões", "26/06: 👗 Irmãs", "27/06: 🙏 Tarde com Deus"],
    "Julho": ["03/07: 🧑‍🎓 Jovens", "10/07: 👔 Varões", "17/07: 🎤 Louvor", "19/07: 🌍 Missões", "24/07: 👗 Irmãs", "25/07: 🙏 Tarde com Deus", "31/07: 🧑‍🎓 Jovens (5ª Sex)"],
    "Agosto": ["07/08: 👔 Varões", "14/08: 🎤 Louvor", "14 e 15/08: 🌍 Congresso Missões", "16/08: 🌍 Missões", "21/08: 👗 Irmãs", "28/08: 🧑‍🎓 Jovens", "29/08: 🙏 Tarde com Deus"],
    "Setembro": ["04/09: 👔 Varões", "11/09: 🎤 Louvor", "18/09: 👗 Irmãs", "20/09: 🌍 Missões", "25/09: 🧑‍🎓 Jovens", "26/09: 🙏 Tarde com Deus"],
    "Outubro": ["02/10: 👔 Varões", "09/10: 🎤 Louvor", "16/10: 👗 Irmãs", "17/10: 💗 Outubro Rosa", "18/10: 🌍 Missões", "23/10: 🧑‍🎓 Jovens", "30/10: 👔 Varões (5ª Sex)", "30 e 31/10: 🎈 Congresso Kids", "31/10: 🙏 Tarde com Deus"],
    "Novembro": ["06/11: 🎤 Louvor", "13/11: 👗 Irmãs", "15/11: 🌍 Missões", "20/11: 🧑‍🎓 Jovens", "21/11: 👑 Conferência Bispa", "27/11: 👔 Varões", "28/11: 🙏 Tarde com Deus"],
    "Dezembro": ["04/12: 🎤 Louvor", "11/12: 👗 Irmãs", "18/12: 🧑‍🎓 Jovens", "20/12: 🌍 Missões", "27/12: 🙏 Tarde com Deus"]
}

# --- 5. LÓGICA DE NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
    st.markdown("<br>", unsafe_allow_html=True)
    c_logo, c_tit = st.columns([1, 3])
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=120)
    with c_tit:
        st.title("ISOSED Cosmópolis")
        st.write("Portal Central de Informações")

    st.markdown("<br>", unsafe_allow_html=True)
    # Coluna central para simetria vertical de início e fim
    col_central = st.columns([1, 5, 1])[1]
    with col_central:
        st.button("🗓️ AGENDA 2026", on_click=navegar, args=("Agenda",))
        st.button("📢 MÍDIA E RECEPÇÃO", on_click=navegar, args=("Escalas",))
        st.button("👥 DEPARTAMENTOS", on_click=navegar, args=("Departamentos",))
        st.button("📖 DEVOCIONAL", on_click=navegar, args=("Devocional",))

elif st.session_state.pagina == "Agenda":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("🗓️ Cronograma Completo 2026")
    for mes, evs in agenda_2026.items():
        with st.expander(f"📅 {mes}"):
            for ev in evs: st.write(f"• {ev}")

elif st.session_state.pagina == "Escalas":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📢 Mídia e Recepção")
    t_mid, t_rec = st.tabs(["📷 Mídia", "🤝 Recepção"])
    
    with t_mid:
        st.subheader("Escala de Fevereiro/2026")
        midia_fev = [
            {"d": "01/02", "op": "Júnior", "ft": "Tiago (17:30)"}, {"d": "04/02", "op": "Lucas", "ft": "Grazi (19:00)"},
            {"d": "06/02", "op": "Samuel", "ft": "Tiago (19:00)"}, {"d": "08/02", "op": "Lucas", "ft": "Grazi (17:30)"},
            {"d": "11/02", "op": "Samuel", "ft": "Tiago (19:00)"}, {"d": "13/02", "op": "Nicholas", "ft": "Grazi (19:00)"},
            {"d": "15/02", "op": "Samuel", "ft": "Tiago (17:30)"}, {"d": "18/02", "op": "Nicholas", "ft": "Grazi (19:00)"},
            {"d": "20/02", "op": "Lucas", "ft": "Tiago (19:00)"}, {"d": "22/02", "op": "Nicholas", "ft": "Grazi (17:30)"},
            {"d": "25/02", "op": "Lucas", "ft": "Tiago (19:00)"}, {"d": "27/02", "op": "Samuel", "ft": "Grazi (19:00)"},
            {"d": "28/02", "op": "Nicholas", "ft": "Tiago (14:30)"}
        ]
        for it in midia_fev:
            st.markdown(f'<div class="card-escala"><b>{it["d"]}</b><br>🎧 Som: {it["op"]} | 📸 Foto: {it["ft"]}</div>', unsafe_allow_html=True)

    with t_rec:
        st.subheader("Escala de Fevereiro/2026")
        recep_fev = [
            {"d": "04/02", "dp": "Ailton e Rita"}, {"d": "06/02", "dp": "Márcia e Felipe"},
            {"d": "08/02", "dp": "Simone e Elisabete"}, {"d": "11/02", "dp": "Ceia e Felipe"},
            {"d": "13/02", "dp": "Ailton e Márcia"}, {"d": "15/02", "dp": "Rita e Simone"},
            {"d": "18/02", "dp": "Ceia e Elisabete"}, {"d": "20/02", "dp": "Felipe e Márcia"},
            {"d": "22/02", "dp": "Ailton e Simone"}, {"d": "28/02", "dp": "Ceia e Rita ✨"}
        ]
        for it in recep_fev:
            st.markdown(f'<div class="card-escala"><b>{it["d"]}</b><br>👥 Dupla: {it["dp"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Departamentos":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("👥 Programação dos Departamentos")
    t_irm, t_jov, t_var, t_mis, t_td = st.tabs(["🌸 Irmãs", "🔥 Jovens", "🛡️ Varões", "🌍 Missões", "🙏 Tarde com Deus"])
    
    with t_irm:
        for m, evs in agenda_2026.items():
            for e in evs:
                if "Irmãs" in e or "Mulheres" in e or "Rosa" in e:
                    st.write(f"📅 **{m}:** {e}")
    with t_jov:
        for m, evs in agenda_2026.items():
            for e in evs:
                if "Jovens" in e or "Retiro" in e:
                    st.write(f"📅 **{m}:** {e}")
    with t_var:
        for m, evs in agenda_2026.items():
            for e in evs:
                if "Varões" in e:
                    st.write(f"📅 **{m}:** {e}")
    with t_mis:
        for m, evs in agenda_2026.items():
            for e in evs:
                if "Missões" in e:
                    st.write(f"📅 **{m}:** {e}")
    with t_td:
        for m, evs in agenda_2026.items():
            for e in evs:
                if "Tarde com Deus" in e:
                    st.write(f"📅 **{m}:** {e}")

elif st.session_state.pagina == "Devocional":
    st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
    st.button("⬅️ VOLTAR AO INÍCIO", on_click=navegar, args=("Início",))
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("📖 Espaço Devocional")
    st.info("Página em desenvolvimento.")
