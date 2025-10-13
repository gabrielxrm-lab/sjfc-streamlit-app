import streamlit as st
import pandas as pd
import data_manager
from datetime import datetime
import os # <-- LINHA ADICIONADA AQUI

# --- LÓGICA DE PERMISSÃO ---
IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'

st.set_page_config(layout="wide", page_title="Gerenciar Jogadores")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

# --- Título e Botão Salvar ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("Gerenciamento de Jogadores")
with c2:
    if st.button("💾 Salvar Alterações na Nuvem", use_container_width=True, type="primary", disabled=not IS_DIRETORIA):
        data_manager.save_data_to_db()

if not IS_DIRETORIA:
    st.warning("🔒 Modo de visualização. Para editar, acesse como Diretoria na página principal.")

# --- Formulário para Adicionar/Editar Jogador (condicional) ---
if IS_DIRETORIA:
    with st.expander("➕ Cadastrar Novo Jogador ou Editar Existente"):
        jogadores_lista = st.session_state.dados.get('players', []); jogadores_nomes = ["Novo Jogador"] + sorted([p['name'] for p in jogadores_lista]); selected_player_name = st.selectbox("Selecione um jogador para editar ou 'Novo Jogador'", jogadores_nomes); player_to_edit = None
        if selected_player_name != "Novo Jogador": player_to_edit = next((p for p in jogadores_lista if p['name'] == selected_player_name), None)
        with st.form("player_form", clear_on_submit=True):
            name = st.text_input("Nome do Jogador", value=player_to_edit['name'] if player_to_edit else ""); position_list = ["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"]; pos_index = position_list.index(player_to_edit['position']) if player_to_edit and player_to_edit.get('position') in position_list else 3; position = st.selectbox("Posição", position_list, index=pos_index); dob = st.text_input("Data Nasc. (DD/MM/AAAA)", value=player_to_edit.get('date_of_birth', '') if player_to_edit else ""); phone = st.text_input("Telefone", value=player_to_edit.get('phone', '') if player_to_edit else "")
            submitted = st.form_submit_button("Adicionar/Atualizar na Lista")
            if submitted:
                if not name or not position: st.error("Nome e Posição são obrigatórios.")
                else:
                    player_data = {'name': name.upper(),'position': position,'date_of_birth': dob, 'phone': phone,'photo_file': player_to_edit.get('photo_file', '') if player_to_edit else ''}
                    if player_to_edit: player_to_edit.update(player_data); st.success(f"Jogador '{name}' atualizado na lista local.")
                    else: player_data['team_start_date'] = datetime.now().strftime('%d/%m/%Y'); st.session_state.dados['players'].append(player_data); st.success(f"Jogador '{name}' adicionado à lista local.")
                    st.info("Lembre-se de salvar as alterações na nuvem."); st.rerun()

# --- Lista de Jogadores ---
st.header("Elenco Atual")
df_players = data_manager.get_players_df()
if not df_players.empty:
    st.dataframe(df_players.drop(columns=['created_at'], errors='ignore'), use_container_width=True, hide_index=True)
    st.write("---"); st.header("🔎 Ficha Detalhada do Jogador")
    player_to_view_name = st.selectbox("Selecione um jogador para ver os detalhes", options=[""] + df_players['name'].tolist(), index=0, placeholder="Escolha um jogador...")
    if player_to_view_name:
        player_data = df_players[df_players['name'] == player_to_view_name].iloc[0].to_dict()
        with st.container(border=True):
            col_img, col_data = st.columns([1, 2]);
            with col_img:
                photo_path = os.path.join(data_manager.PLAYER_PHOTOS_DIR, player_data.get('photo_file', ''));
                if player_data.get('photo_file') and os.path.exists(photo_path): st.image(photo_path, width=200)
                else: st.image("https://via.placeholder.com/200x200.png?text=Sem+Foto", width=200)
            with col_data:
                st.subheader(player_data['name']); st.write(f"**Posição:** {player_data.get('position', 'N/A')}"); st.write(f"**Data Nasc.:** {player_data.get('date_of_birth', 'N/A')}"); st.write(f"**Telefone:** {player_data.get('phone', 'N/A')}"); st.write(f"**No Time Desde:** {player_data.get('team_start_date', 'N/A')}")
    if IS_DIRETORIA:
        st.write("---"); st.header("🗑️ Excluir Jogadores"); players_to_delete_names = st.multiselect("Selecione os jogadores para excluir da lista", df_players['name'].tolist())
        if st.button("Remover Selecionados da Lista", type="secondary"):
            if players_to_delete_names:
                ids_to_delete = df_players[df_players['name'].isin(players_to_delete_names)]['id'].tolist(); data_manager.delete_players_by_ids(ids_to_delete); st.session_state.dados['players'] = [p for p in st.session_state.dados['players'] if p['id'] not in ids_to_delete]; st.warning(f"{len(players_to_delete_names)} jogadores foram removidos. Lembre-se de salvar."); st.rerun()
else:
    st.info("Nenhum jogador cadastrado.")
