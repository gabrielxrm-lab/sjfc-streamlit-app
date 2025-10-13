# data_manager.py
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

ARQUIVO_DADOS = 'player_stats.json'
PLAYER_PHOTOS_DIR = 'player_photos'
SUMULA_LEGACY_DIR = 'sumulas'

# Estrutura de dados padrão
DEFAULT_DATA = {
    'players': [],
    'game_stats': [],
    'monthly_payments': {},
    'game_summaries': {}
}

def initialize_session_state():
    """Inicializa o session_state se ainda não foi feito."""
    if 'dados' not in st.session_state:
        st.session_state['dados'] = load_data()
    # Garante que todas as pastas existam
    os.makedirs(PLAYER_PHOTOS_DIR, exist_ok=True)
    os.makedirs(SUMULA_LEGACY_DIR, exist_ok=True)

def load_data():
    """Carrega os dados do arquivo JSON."""
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Garante que todas as chaves principais existam
                for key in DEFAULT_DATA:
                    if key not in data:
                        data[key] = DEFAULT_DATA[key]
                return data
        except (json.JSONDecodeError, Exception) as e:
            st.error(f"Erro ao ler o arquivo de dados: {e}. Usando dados padrão.")
            return DEFAULT_DATA.copy()
    else:
        st.warning("Arquivo de dados não encontrado. Um novo será criado ao salvar.")
        return DEFAULT_DATA.copy()

def save_data():
    """Salva os dados do session_state no arquivo JSON."""
    if 'dados' in st.session_state:
        try:
            with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
                json.dump(st.session_state['dados'], f, indent=4, ensure_ascii=False)
            st.toast("✅ Dados salvos com sucesso!", icon="💾")
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")

def get_players_df():
    """Retorna um DataFrame do Pandas com os jogadores."""
    if 'dados' in st.session_state and st.session_state['dados']['players']:
        return pd.DataFrame(st.session_state['dados']['players'])
    return pd.DataFrame()

def get_player_by_id(player_id):
    """Busca um jogador pelo seu ID."""
    for player in st.session_state.dados['players']:
        if player['id'] == player_id:
            return player
    return None

def get_player_name_by_id(player_id):
    """Busca o nome de um jogador pelo seu ID."""
    player = get_player_by_id(player_id)
    return player['name'] if player else "Jogador não encontrado"

def generate_new_player_id():
    """Gera um ID único para um novo jogador."""
    return f"player-{int(datetime.now().timestamp())}"