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

# --- 1. FUNÇÕES GLOBAIS ---
def contabilizar_acesso():
    """Lê o valor atual na planilha e soma +1 a cada nova sessão"""
if st.session_state.pagina == "Início":
    # 1. CONTADOR DE ACESSOS
    if 'acesso_contado' not in st.session_state:
        try:
            sh_ac = conectar_planilha()
            aba_ac = sh_ac.worksheet("Acessos")
            total_atual = int(aba_ac.acell('A2').value or 0)
            aba_ac.update_cell(2, 1, total_atual + 1)
            st.session_state.acesso_contado = total_atual + 1
        except: st.session_state.acesso_contado = "---"

    st.markdown("<h2 style='text-align: center;'>ISOSED COSMÓPOLIS</h2>", unsafe_allow_html=True)
    
    # --- NOVIDADE: BUSCA DA PRÓXIMA SANTA CEIA ---
    df_ag = carregar_dados("Agenda")
    prox_ceia_str = None
    if not df_ag.empty:
        # Tenta converter a coluna data
        df_ag['data_dt'] = pd.to_datetime(df_ag['data'], dayfirst=True, errors='coerce')
        # Filtra eventos que contenham "Santa" e que sejam de hoje em diante
        ceias = df_ag[df_ag['evento'].str.contains("Santa", case=False, na=False)]
        proximas = Santa_Ceia[Santa['data_dt'].dt.date >= hoje_br].sort_values(by='data_dt')
        
        if not proximas.empty:
            prox_Santa_Ceia_str = proximas.iloc[0]['data_dt'].strftime('%d/%m/%Y')

    # 2. HORÁRIOS DE CULTO E SANTA CEIA
    # Adicionei a Santa Ceia em destaque logo acima dos horários
    if prox_ceia_str:
        st.markdown(f"""
            <div style="background: linear-gradient(90deg, #b33939, #822727); border-radius: 10px; padding: 15px; text-align: center; margin-bottom: 15px; border: 2px solid #ff5252;">
                <h3 style="margin:0; color: white !important;">🍞 PRÓXIMA SANTA CEIA: {prox_ceia_str} 🍷</h3>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background: rgba(10, 61, 98, 0.4); border: 1px solid #3c6382; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
            <h4 style="margin:0; color:#ffd700; text-align:center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom:10px;">🙏 Nossos Cultos</h4>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Segunda-feira</span> <b>Oração Ministerial</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Quarta-feira</span> <b>Ensino - 19h30</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Sexta-feira</span> <b>Libertação - 19h30</b></div>
            <div style="display: flex; justify-content: space-between; padding: 5px 0;"><span>Domingo</span> <b>Família - 18h00</b></div>
        </div>
    """, unsafe_allow_html=True)

    # 3. ANIVERSARIANTES DA SEMANA
    df_n = carregar_dados("Aniversariantes")
    if not df_n.empty:
        dom_atual = hoje_br - timedelta(days=(hoje_br.weekday() + 1) % 7)
        seg_prox = dom_atual + timedelta(days=8)
        aniv_f = []
        for _, r in df_n.iterrows():
            try:
                d, m = int(r.get('dia', 0)), int(r.get('mes', 0))
                data_aniv = datetime(hoje_br.year, m, d).date()
                if dom_atual <= data_aniv <= seg_prox: aniv_f.append(r)
            except: continue

        if aniv_f:
            st.markdown("<h3 style='text-align: center;'>🎊 Aniversários da Semana</h3>", unsafe_allow_html=True)
            cols = st.columns(len(aniv_f))
            for i, p in enumerate(aniv_f):
                with cols[i]:
                    st.markdown(f'<div class="card-niver"><div class="niver-nome">{p["nome"]}</div><div class="niver-data">{int(p["dia"]):02d}/{int(p["mes"]):02d}</div></div>', unsafe_allow_html=True)

    # 4. MENU PRINCIPAL
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🗓️ Agenda", on_click=navegar, args=("Agenda",), use_container_width=True)
        st.button("👥 Grupos", on_click=navegar, args=("Grupos",), use_container_width=True)
        st.button("🎂 Aniversários", on_click=navegar, args=("AnivMês",), use_container_width=True)
    with c2:
        st.button("📢 Escalas", on_click=navegar, args=("Escalas",), use_container_width=True)
        st.button("📖 Meditar", on_click=navegar, args=("Meditar",), use_container_width=True)
        st.button("📜 Leitura", on_click=navegar, args=("Leitura",), use_container_width=True)

    # 5. LOGO E CONTADOR
    st.markdown("<br>", unsafe_allow_html=True)
    if os.path.exists("logo igreja.png"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo igreja.png", use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-size:0.8em; opacity:0.6;'>Acessos totais: {st.session_state.acesso_contado}</p>", unsafe_allow_html=True)
elif st.session_state.pagina == "Agenda":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🗓️ Agenda ISOSED</h1>", unsafe_allow_html=True)
    
    df = carregar_dados("Agenda")
    
    if not df.empty:
        # Tenta converter a coluna 'data' com segurança
        if 'data' in df.columns:
            df['data_dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        
        nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        abas_agenda = st.tabs(nomes_meses)
        
        for i, aba in enumerate(abas_agenda):
            with aba:
                mes_num = i + 1
                # Filtra os eventos pelo mês da aba
                if 'data_dt' in df.columns:
                    evs = df[df['data_dt'].dt.month == mes_num].sort_values(by='data_dt')
                else:
                    evs = pd.DataFrame() # Caso a coluna data falhe

                if not evs.empty:
                    for _, r in evs.iterrows():
                        # Mostra o evento (usa .get para não dar erro se a coluna mudar)
                        dia_exibicao = r['data_dt'].strftime('%d/%m') if pd.notnull(r['data_dt']) else "S/D"
                        evento_txt = r.get('evento', 'Evento sem nome')
                        
                        st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; 
                                        border-left: 5px solid #0a3d62; margin-bottom: 8px;">
                                <b style="color: #ffd700;">{dia_exibicao}</b> - {evento_txt}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Nenhum evento programado para {nomes_meses[i]}.")
    else:
        st.error("Não foi possível carregar os dados da Agenda. Verifique o nome da aba na planilha.")

elif st.session_state.pagina == "Grupos":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>👥 Departamentos</h1>", unsafe_allow_html=True)
    
    df = carregar_dados("Agenda") # Os grupos usam a mesma base da agenda
    
    if not df.empty:
        if 'data' in df.columns:
            df['data_dt'] = pd.to_datetime(df['data'], dayfirst=True, errors='coerce')
        
        deptos = ["Jovens", "Varões", "Irmãs", "Louvor", "Missões", "Crianças"]
        abas_deptos = st.tabs(deptos)
        
        for i, depto_nome in enumerate(deptos):
            with abas_deptos[i]:
                # Filtra eventos que contenham o nome do departamento (ex: procura "Jovens" em "Culto de Jovens")
                if 'evento' in df.columns:
                    filtro = df[df['evento'].str.contains(depto_nome, case=False, na=False)]
                    if 'data_dt' in df.columns:
                        filtro = filtro.sort_values(by='data_dt')
                else:
                    filtro = pd.DataFrame()

                if not filtro.empty:
                    for _, r in filtro.iterrows():
                        dia_f = r['data_dt'].strftime('%d/%m/%Y') if pd.notnull(r['data_dt']) else "S/D"
                        st.markdown(f"""
                            <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; 
                                        border-left: 5px solid #00b894; margin-bottom: 8px;">
                                <b style="color: #00b894;">{dia_f}</b> — {r.get('evento', '')}
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info(f"Nenhuma atividade encontrada para {depto_nome}.")

elif st.session_state.pagina == "AnivMês":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>🎂 Aniversariantes</h1>", unsafe_allow_html=True)
    df = carregar_dados("Aniversariantes")
    if not df.empty:
        abas = st.tabs(["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"])
        for i, aba in enumerate(abas):
            with aba:
                l = df[pd.to_numeric(df['mes'], errors='coerce') == (i+1)].sort_values(by='dia')
                for _, r in l.iterrows():
                    st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:8px; margin-bottom:5px; border-left:5px solid #f1c40f;"><b style="color:#f1c40f;">Dia {int(r["dia"]):02d}</b> - {r["nome"]}</div>', unsafe_allow_html=True)

elif st.session_state.pagina == "Escalas":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📢 Escalas de Serviço</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📷 Mídia", "🤝 Recepção"])
    with t1:
        df_m = carregar_dados("Midia")
        if not df_m.empty:
            for _, r in df_m.iterrows():
                with st.expander(f"📅 {r.get('data','')} - {r.get('culto','')}"):
                    st.write(f"**Operador:** {r.get('op','')} | **Foto:** {r.get('foto','')} | **Chegada:** {r.get('chegada','')}")
    with t2:
        df_r = carregar_dados("Recepcao")
        if not df_r.empty:
            for _, r in df_r.iterrows():
                with st.expander(f"📅 {r.get('data','')} ({r.get('dia','')})"):
                    st.write(f"**Dupla:** {r.get('dupla','')} | **Chegada:** {r.get('chegada','')}")

elif st.session_state.pagina == "Meditar":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📖 Meditar</h1>", unsafe_allow_html=True)
    d_sel = st.date_input("Escolha a data:", value=hoje_br, format="DD/MM/YYYY")
    df = carregar_dados("Devocional")
    if not df.empty:
        hj = df[df["data"].astype(str).str.strip() == d_sel.strftime('%d/%m/%Y')]
        if not hj.empty:
            d = hj.iloc[0]
            st.markdown(f"**Tema:** {d.get('tema', '')}")
            st.markdown(f"### {d.get('titulo', '')}")
            st.success(f"📖 **Versículo:** {d.get('versiculo', '')}")
            st.write(d.get('texto', ''))
            st.subheader("🎯 Aplicação")
            st.write(d.get('aplicacao', ''))
            st.subheader("💪 Desafio")
            st.write(d.get('desafio', ''))
        else: st.warning("Sem devocional para hoje.")

elif st.session_state.pagina == "Leitura":
    st.button("⬅️ VOLTAR", on_click=navegar, args=("Início",))
    st.markdown("<h1>📜 Área do Leitor</h1>", unsafe_allow_html=True)
    
    if st.session_state.usuario is None:
        aba_ac = st.tabs(["🔐 Entrar", "📝 Cadastrar"])
        with aba_ac[0]:
            ln, ls = st.text_input("Nome:").strip().title(), st.text_input("Senha:", type="password")
            if st.button("Acessar"):
                du = carregar_dados("Usuarios")
                if not du[(du['nome']==ln) & (du['senha'].astype(str)==ls)].empty:
                    st.session_state.usuario = ln
                    st.rerun()
                else: st.error("Erro!")
        with aba_ac[1]:
            with st.form("f_c"):
                n, tel, m, d, s = st.text_input("Nome:"), st.text_input("WhatsApp:"), st.selectbox("Ministério:", ["Louvor", "Irmãs", "Jovens", "Varões", "Mídia", "Visitante"]), st.date_input("Nascimento:", min_value=datetime(1950,1,1)), st.text_input("Senha:", type="password")
                if st.form_submit_button("Ok") and n and s:
                    if salvar_novo_usuario([n, tel, m, str(d), s, 1, "Plano Anual"]): st.success("Ok!")
    else:
        u, df_l, df_p = st.session_state.usuario, carregar_dados("Leitura"), carregar_dados("Progresso")
        if not df_l.empty:
            p_sel = st.selectbox("Plano:", df_l['plano'].unique())
            dia_p = 1
            if not df_p.empty:
                df_p.columns = [str(c).lower().strip() for c in df_p.columns]
                prog = df_p[(df_p['usuario']==u) & (df_p['plano']==p_sel)]
                if not prog.empty: dia_p = int(prog.iloc[0]['dia_atual'])
            
            l_hj = df_l[(df_l['plano']==p_sel) & (pd.to_numeric(df_l['dia'])==dia_p)]
            
            if not l_hj.empty:
                l = l_hj.iloc[0]
                ref = l.get('referencia', '---')
                st.markdown(f"### 📍 Dia {dia_p}")
                
                # Layout da Referência
                st.markdown(f'<div style="background:rgba(10,61,98,0.4); padding:20px; border-radius:15px; border-left:5px solid #00b894; margin-bottom:20px;">{ref}</div>', unsafe_allow_html=True)
                
                with st.spinner('Buscando versículos...'):
                    txts = buscar_capitulos_divididos(ref)
                
                if "Erro" not in txts:
                    abs_b = st.tabs(list(txts.keys()))
                    for i, ab_c in enumerate(abs_b):
                        with ab_c:
                            # CORREÇÃO: white-space: pre-wrap para quebrar as linhas
                            st.markdown(f"""
                                <div style="
                                    text-align: justify; 
                                    line-height: 1.8; 
                                    white-space: pre-wrap; 
                                    background: rgba(255,255,255,0.03); 
                                    padding: 15px; 
                                    border-radius: 10px;
                                    font-size: 1.1em;
                                    color: white;
                                ">
                                    {txts[list(txts.keys())[i]]}
                                </div>
                            """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.info(f"💡 Meditação: {l.get('resumo_para_meditacao', '---')}")
                
                if st.button("✅ Concluir Leitura de Hoje", use_container_width=True):
                    if atualizar_progresso_planilha(u, p_sel, dia_p + 1):
                        st.balloons()
                        st.rerun()
            else:
                st.success("🎉 Parabéns! Plano Concluído!")
                if st.button("Reiniciar Plano"): 
                    atualizar_progresso_planilha(u, p_sel, 1)
                    st.rerun()
        
        st.divider()
        if st.button("Sair da Conta"): 
            st.session_state.usuario = None
            st.rerun()
            # Redes Sociais Fixas no Rodapé de todas as páginas
st.markdown(f"""
    <div class="footer-social">
        <a href="https://www.instagram.com/isosedcosmopolissp/" target="_blank">📸 Instagram</a>
        <a href="https://www.facebook.com/isosedcosmopolissp/" target="_blank">🔵 Facebook</a>
    </div>
    <br><br><br> """, unsafe_allow_html=True)
