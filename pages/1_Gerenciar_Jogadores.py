# pages/1_⚽_Gerenciar_Jogadores.py
import streamlit as st
import pandas as pd
import data_manager
from datetime import datetime
import os
import requests # Usado para listar os arquivos do GitHub

# --- LÓGICA DE PERMISSÃO ---
IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'

# --- CONFIGURAÇÕES DO GITHUB (JÁ PREENCHIDAS PARA VOCÊ) ---
GITHUB_USER = "gabrielxrm-lab"
GITHUB_REPO = "sjfc-streamlit-app"
FOTOS_PATH = "player_photos" # Nome da sua pasta

@st.cache_data(ttl=300) # Cache para não buscar os arquivos toda hora
def get_photo_list_from_github():
    """Busca a lista de nomes de arquivos da pasta de fotos no GitHub."""
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FOTOS_PATH}"
    try:
        response = requests.get(api_url)
        response.raise_for_status() # Lança um erro se a requisição falhar
        files = response.json()
        # Filtra para garantir que são arquivos e não pastas, e pega apenas o nome
        photo_names = [file['name'] for file in files if file['type'] == 'file' and file['name'] != 'manter_pasta.txt']
        return ["Nenhuma"] + sorted(photo_names)
    except Exception as e:
        st.error(f"Não foi possível buscar as fotos do GitHub. Erro: {e}")
        return ["Nenhuma"]

def get_github_image_url(filename):
    """Gera a URL pública da imagem no GitHub."""
    if not filename or filename == "Nenhuma":
        return "https://via.placeholder.com/200x200.png?text=Sem+Foto"
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{FOTOS_PATH}/{filename}"

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

# --- Formulário para Adicionar/Editar Jogador ---
if IS_DIRETORIA:
    with st.expander("➕ Cadastrar Novo Jogador ou Editar Existente"):
        # Busca a lista de fotos diretamente do GitHub
        available_photos = get_photo_list_from_github()

        jogadores_lista = st.session_state.dados.get('players', []); jogadores_nomes = ["Novo Jogador"] + sorted([p['name'] for p in jogadores_lista]); selected_player_name = st.selectbox("Selecione um jogador para editar ou 'Novo Jogador'", jogadores_nomes); player_to_edit = None
        if selected_player_name != "Novo Jogador": player_to_edit = next((p for p in jogadores_lista if p['name'] == selected_player_name), None)
        
        with st.form("player_form", clear_on_submit=True):
            name = st.text_input("Nome do Jogador", value=player_to_edit['name'] if player_to_edit else "")
            position_list = ["GOLEIRO", "ZAGUEIRO", "LATERAL", "MEIO-CAMPO", "ATACANTE"]; pos_index = position_list.index(player_to_edit['position']) if player_to_edit and player_to_edit.get('position') in position_list else 3; position = st.selectbox("Posição", position_list, index=pos_index); dob = st.text_input("Data Nasc. (DD/MM/AAAA)", value=player_to_edit.get('date_of_birth', '') if player_to_edit else ""); phone = st.text_input("Telefone", value=player_to_edit.get('phone', '') if player_to_edit else "")
            
            # Seletor de fotos
            current_photo_file = player_to_edit.get('photo_file', 'Nenhuma') if player_to_edit else 'Nenhuma'
            photo_index = available_photos.index(current_photo_file) if current_photo_file in available_photos else 0
            selected_photo = st.selectbox("Selecione a foto do jogador (da pasta no GitHub)", options=available_photos, index=photo_index)

            submitted = st.form_submit_button("Adicionar/Atualizar na Lista")
            if submitted:
                if not name or not position: st.error("Nome e Posição são obrigatórios.")
                else:
                    photo_filename = selected_photo if selected_photo != "Nenhuma" else ""
                    player_data = {'name': name.upper(),'position': position,'date_of_birth': dob, 'phone': phone,'photo_file': photo_filename}
                    if player_to_edit: player_to_edit.update(player_data); st.success(f"Jogador '{name}' atualizado na lista.")
                    else: player_data['team_start_date'] = datetime.now().strftime('%d/%m/%Y'); st.session_state.dados['players'].append(player_data); st.success(f"Jogador '{name}' adicionado à lista.")
                    st.info("Lembre-se de salvar as alterações na nuvem."); st.rerun()

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
                image_url = get_github_image_url(player_data.get('photo_file'))
                st.image(image_url, width=200)
            with col_data:
                st.subheader(player_data['name']); st.write(f"**Posição:** {player_data.get('position', 'N/A')}"); st.write(f"**Data Nasc.:** {player_data.get('date_of_birth', 'N/A')}"); st.write(f"**Telefone:** {player_data.get('phone', 'N/A')}"); st.write(f"**No Time Desde:** {player_data.get('team_start_date', 'N/A')}")
    
    if IS_DIRETORIA:
        st.write("---"); st.header("🗑️ Excluir Jogadores"); players_to_delete_names = st.multiselect("Selecione para excluir", df_players['name'].tolist())
        if st.button("Remover Selecionados", type="secondary"):
            if players_to_delete_names:
                ids_to_delete = df_players[df_players['name'].isin(players_to_delete_names)]['id'].tolist(); data_manager.delete_players_by_ids(ids_to_delete); st.session_state.dados['players'] = [p for p in st.session_state.dados['players'] if p['id'] not in ids_to_delete]; st.warning(f"{len(players_to_delete_names)} jogadores removidos."); st.rerun()
else:
    st.info("Nenhum jogador cadastrado.")
