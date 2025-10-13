# pages/2_💲_Mensalidades.py
import streamlit as st
import pandas as pd
from datetime import datetime
import data_manager

st.set_page_config(layout="wide", page_title="Mensalidades")
data_manager.initialize_session_state()

st.title("Controle de Mensalidades")

# Seleção de Ano
current_year = datetime.now().year
selected_year = st.selectbox("Selecione o Ano", range(current_year - 2, current_year + 5), index=2)
selected_year_str = str(selected_year)

jogadores = sorted(st.session_state.dados['players'], key=lambda p: p['name'])
if not jogadores:
    st.warning("Nenhum jogador cadastrado. Adicione jogadores na aba 'Gerenciar Jogadores'.")
else:
    # Prepara a estrutura de dados para o DataFrame
    payment_data = []
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    if selected_year_str not in st.session_state.dados['monthly_payments']:
        st.session_state.dados['monthly_payments'][selected_year_str] = {}

    for jogador in jogadores:
        player_id = jogador['id']
        if player_id not in st.session_state.dados['monthly_payments'][selected_year_str]:
            st.session_state.dados['monthly_payments'][selected_year_str][player_id] = {}

        row = {'Jogador': jogador['name']}
        for i, mes in enumerate(meses, 1):
            status = st.session_state.dados['monthly_payments'][selected_year_str][player_id].get(str(i), "Atrasada")
            row[mes] = status == "Paga" # st.data_editor usa True/False para checkboxes
        payment_data.append(row)

    df_payments = pd.DataFrame(payment_data)

    st.info("Clique nas caixas para alterar o status de pagamento (Paga/Atrasada).")

    # Usando o st.data_editor para uma interface editável
    edited_df = st.data_editor(
        df_payments,
        column_config={
            mes: st.column_config.CheckboxColumn(f"{mes}", default=False) for mes in meses
        },
        disabled=["Jogador"],
        use_container_width=True,
        hide_index=True,
        key=f"editor_{selected_year}"
    )

    # Processar as alterações feitas no data_editor
    if not edited_df.equals(df_payments):
        for index, row in edited_df.iterrows():
            player_name = row['Jogador']
            player_id = next((p['id'] for p in jogadores if p['name'] == player_name), None)
            if player_id:
                for i, mes in enumerate(meses, 1):
                    new_status = "Paga" if row[mes] else "Atrasada"
                    st.session_state.dados['monthly_payments'][selected_year_str][player_id][str(i)] = new_status
        st.info("Alterações registradas. Lembre-se de salvar na barra lateral.")