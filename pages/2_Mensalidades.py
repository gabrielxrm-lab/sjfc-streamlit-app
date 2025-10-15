# pages/2_💲_Mensalidades.py
import streamlit as st
import pandas as pd
from datetime import datetime
import data_manager

# --- BLOQUEIO DE ACESSO PARA NÃO-DIRETORIA ---
IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'
if not IS_DIRETORIA:
    st.error("🚫 Acesso Negado!")
    st.warning("Esta página é restrita aos membros da diretoria.")
    st.stop() # Interrompe a execução da página

# --- O restante do código da página continua aqui ---
st.set_page_config(layout="wide", page_title="Mensalidades")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

st.title("Controle de Mensalidades")

c1, c2 = st.columns([1, 3])
with c1:
    current_year = datetime.now().year
    selected_year = st.selectbox("Selecione o Ano", range(current_year - 2, current_year + 5), index=2)
    selected_year_str = str(selected_year)
with c2:
    st.write(""); st.write("")
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary"):
        data_manager.save_data_to_db()

# ... (o resto do arquivo, sem alterações)
