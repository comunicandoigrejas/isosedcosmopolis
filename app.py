import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURAÇÃO DE DATA E FUSO ---
fuso_br = pytz.timezone('America/Sao_Paulo')
agora_br = datetime.now(fuso_br)
hoje_br = agora_br.date()

# Janela de Aniversários: Domingo a Segunda
domingo_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
segunda_proxima = domingo_atual + timedelta(days=8)

st.set_page_config(page_title="ISOSED Cosmópolis", page_icon="⛪", layout="wide")

# --- 2. NAVEGAÇÃO E ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Início"

def navegar(p):
    st.session_state.pagina = p

# --- 3. CONEXÃO COM A PLANILHA ---
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1XSVQH3Aka3z51wPP18JvxNjImLVDxyCWUsVACqFcPK0/edit?usp=sharing"

def carregar_dados(aba):
    try:
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", URL_PLANILHA)
        if match:
            id_plan = match.group(1)
            url = f"https://docs.google.com/spreadsheets/d/{id_plan}/gviz/tq?tqx=out:csv&sheet={aba}"
            df = pd.read_csv(url)
            # Normalização: remove acentos e espaços dos nomes das colunas
            df.columns = [str(c).lower().strip().replace('ê', 'e').replace('ã', 'a').replace('ç', 'c') for c in df.columns]
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 4. ESTILO CSS (Blindagem contra botões brancos e fontes cinzas) ---
st.markdown("""
    <style>
    /* Reset de Fundo e Menus */
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] { visibility: hidden; display: none; }
    [data-testid="stAppViewContainer"] { background-color: #1e1e2f !important; }

    /* FORÇAR TÍTULOS EM BRANCO PURO */
    h1, h2, h3, h4, h5, h6, [data-testid="stMarkdownContainer"] p { 
        color: #FFFFFF !important; 
        font-weight: 800 !important;
    }

    /* ESTILO DOS BOTÕES AZUL ESCURO */
    button[data-testid="stBaseButton-secondary"] {
        width: 150px !important;
        height: 65px !important;
        background-color: #0a3d62 !important; /* Azul Marinho */
        border-radius: 12px !important;
        border: 2px solid #3c6382 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
    }

    /* FORÇAR TEXTO BRANCO DENTRO DOS BOTÕES */
    button[data-testid="stBaseButton-secondary"] p {
        color: #FFFFFF !important; 
        font-weight: 900 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
    }

    /* Cards de Aniversário */
    .card-niver {
        width: 140px !important; height: 90px !important;
        background: rgba(255, 215, 0, 0.1) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 15px !important;
        display: flex !important; flex-direction: column !important;
        align-items: center !important; justify-content: center !important;
        margin: 0 auto !important;
    }
    .niver-nome { font-size: 0.85em !important; font-weight: 900; color: #ffd700 !important; text-transform: uppercase; text-align: center; }
    .niver-data { font-size: 1em !important; font-weight: bold; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LÓGICA DE EXIBIÇÃO (Roteador) ---

if st.session_state.pagina == "Início":
    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)

    # Aniversariantes
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                da = datetime(hoje_br.year, int(r['mes']), int(r['dia'])).date()
                if domingo_atual <= da <= segunda_proxima: aniv_f.append(r)
            except: continue
        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu Principal
    c1, c2, c_logo = st.columns([1.5, 1.5, 2])
    with c1:
        st.button("🗓️ Agenda", key="bt_1", on_click=navegar, args=("Agenda",))
        st.button("👥 Grupos", key="bt_2", on_click=navegar, args=("Grupos",))
        st.button("🎂 Aniversários", key="bt_3", on_click=navegar, args=("AnivMês",))
    with c2:
        st.button("📢 Escalas", key="bt_4", on_click=navegar, args=("Escalas",))
        st.button("📖 Meditar", key="bt_5", on_click=navegar, args=("Meditar",))
        st.button("📜 Leitura", key="bt_6", on_click=navegar, args=("Leitura",))
    with c_logo:
        if os.path.exists("logo igreja.png"): st.image("logo igreja.png", width=200)

elif st.session_state.pagina == "Agenda":
    # Botão de Voltar
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",), key="voltar_ag")
    
    st.markdown("<h1>🗓️ Agenda ISOSED 2026</h1>", unsafe_allow_html=True)
    
    # 1. Carregar os dados
    df = carregar_dados("Agenda")
    
    if not df.empty:
        # Converter a coluna 'data' para o formato de data real do Python
        df['data'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['data']) # Remove linhas sem data
        
        # 2. Criar os botões dos meses em uma linha (Layout de abas)
        meses_lista = {
            1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
        }
        
        # Criar colunas para os botões dos meses
        cols_meses = st.columns(12)
        mes_selecionado = st.session_state.get('mes_agenda', hoje_br.month)

        for i, (num, nome) in enumerate(meses_lista.items()):
            with cols_meses[i]:
                # Se o mês for o selecionado, o botão pode ter um destaque visual
                if st.button(nome, key=f"mes_{num}"):
                    st.session_state.mes_agenda = num
                    st.rerun()

        # 3. Filtrar e Exibir
        mes_final = st.session_state.get('mes_agenda', hoje_br.month)
        eventos_mes = df[df['data'].dt.month == mes_final].sort_values(by='data')

        st.markdown(f"### Eventos de {meses_lista[mes_final]}")
        
        if not eventos_mes.empty:
            for _, r in eventos_mes.iterrows():
                # Formata a exibição: Dia - Evento
                dia_formatado = r['data'].strftime('%d/%m')
                st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 5px solid #0a3d62;">
                        <span style="color: #ffd700; font-weight: bold;">{dia_formatado}</span> - 
                        <span style="color: white;">{r['evento']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"Nenhum evento agendado para {meses_lista[mes_final]}.")
    else:
        st.error("⚠️ Não foi possível carregar os dados da aba 'Agenda'. Verifique o nome da aba na planilha.")

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    
    with t1:
        df_m = carregar_dados("Midia")
        if not df_m.empty:
            for _, r in df_m.iterrows():
                with st.expander(f"📅 {r.get('data','')} - {r.get('culto','')}"):
                    st.write(f"**Operador:** {r.get('op','')}")
                    st.write(f"**Foto:** {r.get('foto','')}")
                    st.write(f"**Chegada:** {r.get('chegada','')}")
    with t2:
        df_r = carregar_dados("Recepcao")
        if not df_r.empty:
            for _, r in df_r.iterrows():
                with st.expander(f"📅 {r.get('data','')} ({r.get('dia','')})"):
                    st.write(f"**Dupla:** {r.get('dupla','')}")
                    st.write(f"**Chegada:** {r.get('chegada','')}")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        dt_str = d_sel.strftime('%d/%m/%Y')
        hj = df[df["data"].astype(str).str.strip() == dt_str]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"**Tema:** {d.get('tema', '')}")
            st.markdown(f"### {d.get('titulo', '')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
            st.markdown("---")
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', ''))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', ''))
        else: st.warning("Sem devocional para esta data.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Plano de Leitura</h1>", unsafe_allow_html=True)
    df_l = carregar_dados("Leitura")
    if not df_l.empty:
        # Mostra a leitura sugerida para o dia atual
        hoje_l = df_l[df_l['dia'].astype(str) == str(hoje_br.day)]
        if not hoje_l.empty:
            l = hoje_l.iloc[0]
            st.info(f"📍 **Plano:** {l.get('plano', 'Anual')}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"📖 **Antigo Testamento:** {l.get('antigo_testamento','')}")
                st.write(f"📖 **Novo Testamento:** {l.get('novo_testamento','')}")
            with col2:
                st.write(f"🎶 **Salmos:** {l.get('salmos','')}")
                st.write(f"💡 **Provérbios:** {l.get('proverbios','')}")
        st.divider()
        st.dataframe(df_l, use_container_width=True)

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Grupos e Departamentos</h1>", unsafe_allow_html=True)

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes do Mês</h1>", unsafe_allow_html=True)
