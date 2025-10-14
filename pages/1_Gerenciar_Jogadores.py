# pages/1_⚽_Gerenciar_Jogadores.py
import streamlit as st
import pandas as pd
import data_manager
from datetime import datetime
import os

st.set_page_config(layout="wide", page_title="Gerenciar Jogadores")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

# --- Título e Botão Salvar ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Gerenciamento de Jogadores")
with c2:
    if st.button("💾 Salvar Alterações na Nuvem", width='stretch', type="primary"):
        data_manager.save_data_to_db()

st.info("Adicione, edite ou remova jogadores. Lembre-se de salvar as alterações na nuvem.")

# --- Formulário para Adicionar/Editar Jogador ---
with st.expander("➕ Cadastrar Novo Jogador ou Editar Existente", expanded=False):
    jogadores_lista = st.session_state.dados.get('players', [])
    jogadores_nomes = ["Novo Jogador"] + sorted([p['name'] for p in jogadores_lista])
    
    selected_player_name = st.selectbox("Selecione um jogador para editar ou 'Novo Jogador'", jogadores_nomes)

    player_to_edit = None
    if selected_player_name != "Novo Jogador":
        player_to_edit = next((p for p in jogadores_lista if p['name'] == selected_player_name), None)

    with st.form("player_form"):
        name = st.text_input("Nome do Jogador", value=player_to_edit['name'] if player_to_edit else "")
        position_list = ["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"]; pos_index = position_list.index(player_to_edit['position']) if player_to_edit and player_to_edit.get('position') in position_list else 3; position = st.selectbox("Posição", position_list, index=pos_index); dob = st.text_input("Data Nasc. (DD/MM/AAAA)", value=player_to_edit.get('date_of_birth', '') if player_to_edit else ""); phone = st.text_input("Telefone", value=player_to_edit.get('phone', '') if player_to_edit else "")
        uploaded_photo = st.file_uploader("Alterar Foto do Jogador (.png, .jpg)", type=['png', 'jpg', 'jpeg'])
        current_photo_identifier = player_to_edit.get('photo_file', '') if player_to_edit else ''
        if current_photo_identifier and current_photo_identifier.startswith('http'):
            st.caption("Foto atual:"); st.image(current_photo_identifier, width=100)
        
        submitted = st.form_submit_button("Adicionar/Atualizar Jogador")
        if submitted:
            if not name or not position: st.error("Nome e Posição são obrigatórios.")
            else:
                photo_identifier = current_photo_identifier
                if uploaded_photo is not None:
                    file_bytes = uploaded_photo.getvalue(); file_path_in_bucket = f"fotos_jogadores/{name.replace(' ', '-').lower()}.{uploaded_photo.name.split('.')[-1]}"; photo_identifier = data_manager.upload_file_to_storage(file_bytes, file_path_in_bucket)
                
                player_data = {'name': name.upper(),'position': position,'date_of_birth': dob, 'phone': phone,'photo_file': photo_identifier}
                
                if player_to_edit:
                    player_to_edit.update(player_data)
                    st.success(f"Jogador '{name}' atualizado na lista. Clique em 'Salvar' para persistir.")
                    st.rerun()
                else:
                    player_data['team_start_date'] = datetime.now().strftime('%d/%m/%Y')
                    st.session_state.dados['players'].append(player_data)
                    st.success(f"Novo jogador '{name}' adicionado. Salvando no banco de dados...")
                    # Força o salvamento imediato para obter o ID
                    data_manager.save_data_to_db()
                    # O save_data_to_db já faz o rerun, então não é necessário aqui.

# --- Lista de Jogadores e Ficha ---
st.header("Elenco Atual")
df_players = data_manager.get_players_df()
if not df_players.empty:
    st.dataframe(df_players.drop(columns=['created_at', 'photo_file'], errors='ignore'), use_container_width=True, hide_index=True)
    st.write("---"); st.header("🔎 Ficha Detalhada do Jogador")
    player_to_view_name = st.selectbox("Selecione um jogador para ver os detalhes", options=[""] + df_players['name'].tolist(), index=0, placeholder="Escolha um jogador...")
    if player_to_view_name:
        player_data = df_players[df_players['name'] == player_to_view_name].iloc[0].to_dict()
        with st.container(border=True):
            col_img, col_data = st.columns([1, 2]);
            with col_img:
                photo_identifier = player_data.get('photo_file', '');
                if photo_identifier and photo_identifier.startswith('http'): st.image(photo_identifier, width=200)
                else: st.image("https://via.placeholder.com/200x200.png?text=Sem+Foto", width=200)
            with col_data:
                st.subheader(player_data['name']); st.write(f"**Posição:** {player_data.get('position', 'N/A')}"); st.write(f"**Data Nasc.:** {player_data.get('date_of_birth', 'N/A')}"); st.write(f"**Telefone:** {player_data.get('phone', 'N/A')}"); st.write(f"**No Time Desde:** {player_data.get('team_start_date', 'N/A')}")
    st.write("---"); st.header("🗑️ Excluir Jogadores"); players_to_delete_names = st.multiselect("Selecione os jogadores para excluir da lista", df_players['name'].tolist())
    if st.button("Remover Selecionados da Lista", type="secondary"):
        if players_to_delete_names:
            ids_to_delete = df_players[df_players['name'].isin(players_to_delete_names)]['id'].tolist(); data_manager.delete_players_by_ids(ids_to_delete); st.session_state.dados['players'] = [p for p in st.session_state.dados['players'] if 'id' in p and p['id'] not in ids_to_delete]; st.warning(f"{len(players_to_delete_names)} jogadores foram removidos. Lembre-se de salvar."); st.rerun()
else:
    st.info("Nenhum jogador cadastrado.")
