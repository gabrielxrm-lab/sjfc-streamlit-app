# pages/2_💲_Mensalidades.py
import streamlit as st
import pandas as pd
from datetime import datetime
import data_manager

st.set_page_config(layout="wide", page_title="Mensalidades")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

st.title("Controle de Mensalidades")

# --- Seletor de Ano ---
current_year = datetime.now().year
selected_year = st.selectbox("Selecione o Ano", range(current_year - 2, current_year + 5), index=2)
selected_year_str = str(selected_year)

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

    st.info("Clique nas caixas para alterar o status (marcado = Paga). Salve na barra lateral.")
    
    if not df_payments.empty:
        # A tabela agora está sempre habilitada para edição
        edited_df = st.data_editor(
            df_payments,
            column_config={
                "player_id": None, 
                **{mes: st.column_config.CheckboxColumn(f"{mes}", default=False) for mes in meses}
            },
            disabled=False, # <-- MUDANÇA PRINCIPAL AQUI
            use_container_width=True, 
            hide_index=True, 
            key=f"editor_{selected_year}"
        )

        if not edited_df.equals(df_payments):
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
