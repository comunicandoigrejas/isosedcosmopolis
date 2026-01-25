import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="App ISOSED Cosmópolis", layout="wide")

# 2. ESTILIZAÇÃO CSS (Fundo Degradê e Ajustes)
# Aqui definimos o degradê de verde para azul
st.markdown("""
    <style>
    /* Fundo da página principal */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #00b09b 0%, #302b63 100%);
        color: white;
    }

    /* Fundo da barra lateral */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Ajuste de cor dos textos para legibilidade */
    h1, h2, h3, p, span {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGO NA BARRA LATERAL
# Certifique-se de ter um arquivo chamado 'logo.png' na mesma pasta do código
# Se não tiver o arquivo ainda, você pode usar uma URL de imagem
try:
    st.sidebar.image("logo igreja.png", width=150)
except:
    st.sidebar.title("⛪ ISOSED")

st.sidebar.markdown("---")

# 4. NAVEGAÇÃO
menu = st.sidebar.radio("Navegação Principal", 
    ["Início", "Agenda 2026", "Redes Sociais", "Departamentos", "Devocional Diário"])

# --- LÓGICA DAS PÁGINAS ---

if menu == "Início":
    st.title("Bem-vindo ao Portal ISOSED")
    st.write("Central de informações da Igreja Só o Senhor é Deus em Cosmópolis.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📅 Próximo Culto: Domingo às 19:00h")
    with col2:
        st.success("🙏 Pedido de Oração: Use a aba Devocional")

elif menu == "Departamentos":
    st.header("Nossos Departamentos")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Jovens", "Crianças", "Mulheres", "Varões", "Missões"])
    
    with tab1:
        st.subheader("Departamento de Jovens")
        st.write("Acompanhe aqui a escala e os eventos da mocidade.")

# Os outros menus seguem a mesma lógica...
