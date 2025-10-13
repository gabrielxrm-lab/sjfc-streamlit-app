# pages/2_💲_Mensalidades.py
import streamlit as st
import pandas as pd
from datetime import datetime
import data_manager

# --- LÓGICA DE PERMISSÃO ---
IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'

st.set_page_config(layout="wide", page_title="Mensalidades")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

st.title("Controle de Mensalidades")
if not IS_DIRETORIA:
    st.warning("🔒 Modo de visualização. Para editar, acesse como Diretoria na página principal.")

# --- Seletor de Ano e Botão Salvar ---
c1, c2 = st.columns([1, 3])
with c1:
    current_year = datetime.now().year
    selected_year = st.selectbox("Selecione o Ano", range(current_year - 2, current_year + 5), index=2)
    selected_year_str = str(selected_year)
with c2:
    st.write("") # Apenas para alinhamento vertical
    st.write("")
    if IS_DIRETORIA:
        # A chamada para salvar os dados deve estar DENTRO deste "if".
        if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary"):
            data_manager.save_data_to_db() # <-- CORREÇÃO APLICADA AQUI

# --- Tabela de Mensalidades ---
jogadores = st.session_state.dados.get('players', [])
if not jogadores:
    st.warning("Nenhum jogador cadastrado.")
else:
    player_id_to_name = {str(p['id']): p['name'] for p in jogadores}
    payment_data = []
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    payments_this_year = st.session_state.dados.get('monthly_payments', {}).get(selected_year_str, {})
    
    for player_id_str, player_name in player_id_to_name.items():
        row = {'Jogador': player_name, 'player_id': player_id_str}
        player_payments = payments_this_year.get(player_id_str, {})
        for i, mes in enumerate(meses, 1):
            status = player_payments.get(str(i), "Atrasada")
            row[mes] = (status == "Paga")
        payment_data.append(row)

    df_payments = pd.DataFrame(payment_data)

    if IS_DIRETORIA:
        st.info("Clique nas caixas para alterar o status. Lembre-se de salvar na barra lateral.")
    
    if not df_payments.empty:
        edited_df = st.data_editor(
            df_payments,
            column_config={
                "player_id": None, 
                **{mes: st.column_config.CheckboxColumn(f"{mes}", default=False) for mes in meses}
            },
            disabled=not IS_DIRETORIA,
            use_container_width=True, 
            hide_index=True, 
            key=f"editor_{selected_year}"
        )

        if IS_DIRETORIA and not edited_df.equals(df_payments):
            for index, row in edited_df.iterrows():
                player_id_str = str(row['player_id'])
                if selected_year_str not in st.session_state.dados['monthly_payments']:
                    st.session_state.dados['monthly_payments'][selected_year_str] = {}
                if player_id_str not in st.session_state.dados['monthly_payments'][selected_year_str]:
                    st.session_state.dados['monthly_payments'][selected_year_str][player_id_str] = {}
                for i, mes in enumerate(meses, 1):
                    new_status = "Paga" if row[mes] else "Atrasada"
                    st.session_state.dados['monthly_payments'][selected_year_str][player_id_str][str(i)] = new_status
            st.toast("Alterações registradas na lista. Não esqueça de salvar!")
