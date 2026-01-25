import streamlit as st

# Configuração da página
st.set_page_config(page_title="App Igreja", layout="wide")

# --- SIDEBAR NAVEGAÇÃO ---
st.sidebar.title("Navegação")
menu = st.sidebar.radio("Ir para:", ["Home", "Agenda", "Redes Sociais", "Departamentos", "Devocional"])

# --- ÁREA HOME ---
if menu == "Home":
    st.header("Bem-vindo ao App da nossa Igreja")
    st.info("Próximo Culto: Domingo às 19:00h")
    # Espaço para Versículo do Dia

# --- ÁREA DEPARTAMENTOS ---
elif menu == "Departamentos":
    st.header("Departamentos")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Jovens", "Crianças", "Mulheres", "Varões", "Missões"])
    
    with tab1:
        st.subheader("Departamento de Jovens")
        st.write("Informações sobre o próximo congresso...")
    # Repetir para as outras abas...

# --- ÁREA REDES SOCIAIS ---
elif menu == "Redes Sociais":
    st.header("Gestão de Mídia")
    # Aqui você pode integrar o código do seu app de legendas
