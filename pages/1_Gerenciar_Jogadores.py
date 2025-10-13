# pages/1_⚽_Gerenciar_Jogadores.py
import streamlit as st
import pandas as pd
import data_manager
import os
from datetime import datetime

st.set_page_config(layout="wide", page_title="Gerenciar Jogadores")
data_manager.initialize_session_state()

st.title("Gerenciamento de Jogadores")

# --- Formulário para Adicionar/Editar Jogador ---
with st.expander("➕ Cadastrar Novo Jogador ou Editar Existente", expanded=False):
    jogadores_nomes = ["Novo Jogador"] + sorted([p['name'] for p in st.session_state.dados['players']])
    selected_player_name = st.selectbox("Selecione um jogador para editar ou escolha 'Novo Jogador' para cadastrar", jogadores_nomes)

    player_to_edit = None
    if selected_player_name != "Novo Jogador":
        player_to_edit = next((p for p in st.session_state.dados['players'] if p['name'] == selected_player_name), None)

    with st.form("player_form", clear_on_submit=True):
        name = st.text_input("Nome do Jogador", value=player_to_edit['name'] if player_to_edit else "")
        position = st.selectbox("Posição", ["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"],
                                index=["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"].index(player_to_edit['position']) if player_to_edit else 3)
        dob = st.text_input("Data Nasc. (DD/MM/AAAA)", value=player_to_edit.get('date_of_birth', '') if player_to_edit else "")
        phone = st.text_input("Telefone", value=player_to_edit.get('phone', '') if player_to_edit else "")

        uploaded_photo = st.file_uploader("Foto do Jogador (.png, .jpg)", type=['png', 'jpg', 'jpeg'])
        current_photo = player_to_edit.get('photo_file', '') if player_to_edit else ''
        if current_photo:
            st.caption(f"Foto atual: {current_photo}")


        submitted = st.form_submit_button("Salvar Jogador")
        if submitted:
            if not name or not position:
                st.error("Nome e Posição são obrigatórios.")
            else:
                photo_filename = current_photo
                if uploaded_photo is not None:
                    photo_filename = uploaded_photo.name
                    dest_path = os.path.join(data_manager.PLAYER_PHOTOS_DIR, photo_filename)
                    with open(dest_path, "wb") as f:
                        f.write(uploaded_photo.getbuffer())

                if player_to_edit:
                    player_to_edit.update({
                        'name': name.upper(), 'position': position, 'date_of_birth': dob,
                        'phone': phone, 'photo_file': photo_filename
                    })
                    st.success(f"Jogador '{name}' atualizado!")
                else:
                    new_player = {
                        "id": data_manager.generate_new_player_id(), "name": name.upper(), "position": position,
                        "date_of_birth": dob, "phone": phone, "photo_file": photo_filename,
                        "team_start_date": datetime.now().strftime('%d/%m/%Y')
                    }
                    st.session_state.dados['players'].append(new_player)
                    st.success(f"Jogador '{name}' cadastrado!")
                
                st.info("Lembre-se de salvar as alterações na barra lateral.")
                st.rerun()

# --- Lista de Jogadores ---
st.header("Elenco Atual")
df_players = data_manager.get_players_df()

if not df_players.empty:
    col1, col2 = st.columns(2)
    filter_name = col1.text_input("Filtrar por nome")
    filter_pos = col2.selectbox("Filtrar por posição", ["Todos"] + sorted(df_players['position'].unique().tolist()))

    filtered_df = df_players
    if filter_name:
        filtered_df = filtered_df[filtered_df['name'].str.contains(filter_name, case=False)]
    if filter_pos != "Todos":
        filtered_df = filtered_df[filtered_df['position'] == filter_pos]

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.header("🔎 Ficha Detalhada do Jogador")
    if not filtered_df.empty:
        player_to_view = st.selectbox("Selecione um jogador para ver os detalhes", filtered_df['name'].tolist())
        if player_to_view:
            player_data = filtered_df[filtered_df['name'] == player_to_view].iloc[0].to_dict()
            col1, col2 = st.columns([1, 2])
            with col1:
                photo_path = os.path.join(data_manager.PLAYER_PHOTOS_DIR, player_data.get('photo_file', ''))
                if os.path.exists(photo_path):
                    st.image(photo_path, caption=player_data['name'], width=200)
                else:
                    st.caption("[Sem Foto]")
            with col2:
                st.subheader(player_data['name'])
                st.write(f"**Posição:** {player_data.get('position', 'N/A')}")
                st.write(f"**Data Nasc.:** {player_data.get('date_of_birth', 'N/A')}")
                st.write(f"**Telefone:** {player_data.get('phone', 'N/A')}")
                st.write(f"**No Time Desde:** {player_data.get('team_start_date', 'N/A')}")
    
    st.write("---")
    st.header("🗑️ Excluir Jogadores")
    players_to_delete = st.multiselect("Selecione os jogadores para excluir", df_players['name'].tolist())
    if st.button("Excluir Selecionados", type="secondary"):
        if players_to_delete:
            ids_to_delete = df_players[df_players['name'].isin(players_to_delete)]['id'].tolist()
            st.session_state.dados['players'] = [p for p in st.session_state.dados['players'] if p['id'] not in ids_to_delete]
            st.warning(f"{len(players_to_delete)} jogadores foram excluídos. Salve as alterações.")
            st.rerun()
else:
    st.info("Nenhum jogador cadastrado.")
