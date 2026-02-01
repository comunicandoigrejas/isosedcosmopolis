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

# --- 3. ESTILIZAÇÃO CSS (Fundo, Botões Padronizados e Tabelas) ---
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }
    [data-testid="stSidebar"] { display: none; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #ffffff !important; }

    /* Botões do Hub Central - Tamanho Único */
    div.stButton > button {
        width: 100%;
        height: 120px;
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        font-size: 22px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00ffcc;
        color: #302b63;
        transform: scale(1.02);
    }
    .card-congresso {
        background: rgba(255, 215, 0, 0.2);
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #ffd700;
        margin-bottom: 20px;
    }
    .data-item {
        background: rgba(0, 0, 0, 0.3);
        padding: 8px 15px;
        border-radius: 5px;
        margin-bottom: 5px;
        border-left: 3px solid #00ffcc;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DADOS (Agenda e Escala de Mídia) ---
agenda_completa = {
    "Janeiro":   {"Jovens": "16/01", "Varões": "23/01", "Louvor": "30/01"},
    "Fevereiro": {"Irmãs": "06/02", "Jovens": "13/02", "Varões": "20/02", "Louvor": "27/02"},
    "Março":     {"Irmãs": "06/03", "Jovens": "13/03", "Varões": "20/03", "Louvor": "27/03"},
    "Abril":     {"Irmãs": "03/04", "Jovens": "10/04", "Varões": "17/04", "Louvor": "24/04"},
    "Maio":      {"Irmãs": "01/05 e 29/05", "Jovens": "08/05", "Varões": "15/05", "Louvor": "22/05"}
}

# Dados extraídos das imagens enviadas
dados_escala_midia = [
    {"Data": "01/02", "Dia": "Dom", "Culto": "Família", "Operador": "Júnior", "Fotógrafo": "Tiago (17:30)"},
    {"Data": "04/02", "Dia": "Qua", "Culto": "Culto", "Operador": "Lucas", "Fotógrafo": "Grazi (19:00)"},
    {"Data": "06/02", "Dia": "Sex", "Culto": "Culto", "Operador": "Samuel", "Fotógrafo": "Tiago (19:00)"},
    {"Data": "08/02", "Dia": "Dom", "Culto": "Santa Ceia", "Operador": "Lucas", "Fotógrafo": "Grazi (17:30)"},
    {"Data": "11/02", "Dia": "Qua", "Culto": "Culto", "Operador": "Samuel", "Fotógrafo": "Tiago (19:00)"},
    {"Data": "13/02", "Dia": "Sex", "Culto": "Culto", "Operador": "Nicholas", "Fotógrafo": "Grazi (19:00)"},
    {"Data": "15/02", "Dia": "Dom", "Culto": "Missões", "Operador": "Samuel", "Fotógrafo": "Tiago (17:30)"},
    {"Data": "18/02", "Dia": "Qua", "Culto": "Culto", "Operador": "Nicholas", "Fotógrafo": "Grazi (19:00)"},
    {"Data": "20/02", "Dia": "Sex", "Culto": "Culto", "Operador": "Lucas", "Fotógrafo": "Tiago (19:00)"},
    {"Data": "22/02", "Dia": "Dom", "Culto": "Família", "Operador": "Nicholas", "Fotógrafo": "Grazi (17:30)"},
    {"Data": "25/02", "Dia": "Qua", "Culto": "Culto", "Operador": "Lucas", "Fotógrafo": "Tiago (19:00)"},
    {"Data": "27/02", "Dia": "Sex", "Culto": "Culto", "Operador": "Samuel", "Fotógrafo": "Grazi (19:00)"},
    {"Data": "28/02", "Dia": "Sáb", "Culto": "Tarde com Deus", "Operador": "Nicholas", "Fotógrafo": "Tiago (14:30)"}
]

# --- 5. LÓGICA DE NAVEGAÇÃO ---

if st.session_state.pagina == "Início":
