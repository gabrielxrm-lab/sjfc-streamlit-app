# Home.py
import streamlit as st
import data_manager
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Central do São Jorge FC",
    page_icon="🛡️",
    layout="wide"
)

# --- Inicialização dos Dados ---
data_manager.initialize_session_state()

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    logo_path = "logo_sao_jorge.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    
    st.title("São Jorge FC")
    st.write("---")
    
    # Botão de salvar fica sempre visível
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary"):
        data_manager.save_data_to_db()

# --- Página Principal ---
st.title("🛡️ Central de Dados do São Jorge FC")
st.markdown("##### // Monitoramento de Performance de Atletas //")
st.write("---")
st.success("Bem-vindo! O acesso está aberto para visualização e edição.")
st.info("Use o menu na barra lateral para navegar. Lembre-se de salvar suas alterações.")
