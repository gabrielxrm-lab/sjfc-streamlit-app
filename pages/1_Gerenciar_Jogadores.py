# pages/1_⚽_Gerenciar_Jogadores.py
import streamlit as st
import pandas as pd
import data_manager
import os
from datetime import datetime

st.set_page_config(layout="wide", page_title="Gerenciar Jogadores")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

# --- Título ---
st.title("Gerenciamento de Jogadores")
st.info("Adicione, edite ou remova jogadores. Lembre-se de salvar as alterações na barra lateral.")

# --- Formulário para Adicionar/Editar Jogador ---
with st.expander("➕ Cadastrar Novo Jogador ou Editar Existente", expanded=False):
    jogadores_lista = st.session_state.dados.get('players', [])
    jogadores_nomes = ["Novo Jogador"] + sorted([p['name'] for p in jogadores_lista])
    
    selected_player_name = st.selectbox("Selecione um jogador para editar ou 'Novo Jogador'", jogadores_nomes)

    player_to_edit = None
    if selected_player_name != "Novo Jogador":
        player_to_edit = next((p for p in jogadores_lista if p['name'] == selected_player_name), None)

    with st.form("player_form", clear_on_submit=True):
        name = st.text_input("Nome do Jogador", value=player_to_edit['name'] if player_to_edit else "")
        position_list = ["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"]
        pos_index = position_list.index(player_to_edit['position']) if player_to_edit and player_to_edit.get('position') in position_list else 3
        position = st.selectbox("Posição", position_list, index=pos_index)
        dob = st.text_input("Data Nasc. (DD/MM/AAAA)", value=player_to_edit.get('date_of_birth', '') if player_to_edit else "")
        phone = st.text_input("Telefone", value=player_to_edit.get('phone', '') if player_to_edit else "")
        
        # --- CAMPO DE UPLOAD DE FOTO REINTEGRADO ---
        uploaded_photo = st.file_uploader("Foto do Jogador (.png, .jpg)", type=['png', 'jpg', 'jpeg'])
        current_photo = player_to_edit.get('photo_file', '') if player_to_edit else ''
        if current_photo:
            st.caption(f"Foto atual: {current_photo}")
        
        submitted = st.form_submit_button("Adicionar/Atualizar na Lista")
        if submitted:
            if not name or not position: st.error("Nome e Posição são obrigatórios.")
            else:
                # --- LÓGICA PARA SALVAR A FOTO ---
                photo_filename = current_photo
                if uploaded_photo is not None:
                    # Se uma nova foto foi enviada, salva ela na pasta
                    photo_filename = uploaded_photo.name
                    dest_path = os.path.join(data_manager.PLAYER_PHOTOS_DIR, photo_filename)
                    with open(dest_path, "wb") as f:
                        f.write(uploaded_photo.getbuffer())
                    st.toast(f"Foto '{photo_filename}' salva localmente.")
                
                # Prepara os dados do jogador com o nome do arquivo da foto
                player_data = {
                    'name': name.upper(), 'position': position, 'date_of_birth': dob, 
                    'phone': phone, 'photo_file': photo_filename
                }
                
                if player_to_edit: 
                    player_to_edit.update(player_data)
                    st.success(f"Jogador '{name}' atualizado na lista local.")
                else: 
                    player_data['team_start_date'] = datetime.now().strftime('%d/%m/%Y')
                    st.session_state.dados['players'].append(player_data)
                    st.success(f"Jogador '{name}' adicionado à lista local.")
                
                st.info("Lembre-se de salvar as alterações na nuvem.")
                st.rerun()

# --- Lista de Jogadores ---
st.header("Elenco Atual")
df_players = data_manager.get_players_df()

if not df_players.empty:
    st.dataframe(df_players.drop(columns=['created_at'], errors='ignore'), use_container_width=True, hide_index=True)
    
    # --- Seção de Exclusão ---
    st.write("---")
    st.header("🗑️ Excluir Jogadores")
    players_to_delete_names = st.multiselect("Selecione os jogadores para excluir da lista", df_players['name'].tolist())
    
    if st.button("Remover Selecionados da Lista", type="secondary"):
        if players_to_delete_names:
            ids_to_delete = df_players[df_players['name'].isin(players_to_delete_names)]['id'].tolist()
            data_manager.delete_players_by_ids(ids_to_delete)
            st.session_state.dados['players'] = [p for p in st.session_state.dados['players'] if p['id'] not in ids_to_delete]
            st.warning(f"{len(players_to_delete_names)} jogadores foram removidos. Lembre-se de salvar.")
            st.rerun()
else:
    st.info("Nenhum jogador cadastrado.")
