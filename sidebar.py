# sidebar.py
import streamlit as st
import data_manager
import os

def create_sidebar():
    """
    Cria a barra lateral, aplicando o CSS global e gerenciando o login e a navegação.
    """
    
    # --- CSS GLOBAL (INCLUINDO A REGRA PARA ESCONDER O MENU AUTOMÁTICO) ---
    st.markdown(
        """
        <style>
            /* Esconde o menu de navegação automático do Streamlit */
            [data-testid="stSidebarNav"] > ul {
                display: none;
            }
            /* Fixa a barra lateral */
            section[data-testid="stSidebar"] {
                width: 300px;
                position: fixed;
                height: 100%;
                top: 0;
                left: 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # --- Lógica de Perfil e Login ---
    if 'role' not in st.session_state: 
        st.session_state.role = 'Jogador'

    st.sidebar.title("Perfil de Acesso")
    profile = st.sidebar.radio(
        "Selecione seu perfil:", 
        ('Jogador', 'Diretoria'), 
        index=0 if st.session_state.role == 'Jogador' else 1
    )

    if profile == 'Diretoria':
        if st.session_state.role == 'Diretoria':
            st.sidebar.success("Logado como Diretoria.")
            if st.sidebar.button("Sair do modo Edição"):
                st.session_state.role = 'Jogador'
                st.rerun()
        else:
            password = st.sidebar.text_input("Senha da Diretoria:", type="password")
            if st.sidebar.button("Entrar como Diretoria"):
                creds = st.secrets.get("credentials", {})
                correct_password = creds.get("diretoria_password")
                if correct_password and password == correct_password:
                    st.session_state.role = 'Diretoria'
                    st.rerun()
                else:
                    st.sidebar.error("Senha incorreta ou não configurada.")
    else:
        if st.session_state.role == 'Diretoria':
            st.session_state.role = 'Jogador'
            st.rerun()
        else:
            st.session_state.role = 'Jogador'

    IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'

    # --- Menu de Navegação ---
    st.sidebar.write("---")
    st.sidebar.page_link("Home.py", label="🏠 Página Principal")
    st.sidebar.page_link("pages/1_Gerenciar_Jogadores.py", label="⚽ Gerenciar Jogadores")
    if IS_DIRETORIA:
        st.sidebar.page_link("pages/2_Mensalidades.py", label="💲 Mensalidades")
    st.sidebar.page_link("pages/Nova_Súmula.py", label="📋 Nova Súmula")
    st.sidebar.page_link("pages/sorteio_de_times.py", label="🎲 Sorteio de Times")
    st.sidebar.page_link("pages/Ranking.py", label="🏆 Ranking")

    # --- Rodapé da Barra Lateral ---
    st.sidebar.write("---")
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path):
        st.sidebar.image(logo_path, width=150)
    st.sidebar.title("São Jorge FC")
    st.sidebar.write("---")
    st.sidebar.caption("Desenvolvido por:")
    st.sidebar.markdown("**Gabriel Conrado**")
    st.sidebar.caption("📱 (21) 97275-7256")
