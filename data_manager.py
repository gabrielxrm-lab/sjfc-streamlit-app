# data_manager.py
import streamlit as st
import os
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- Configurações ---
PLAYER_PHOTOS_DIR = 'player_photos'
SUMULA_LEGACY_DIR = 'sumulas'

# --- Conexão com Supabase ---
@st.cache_resource
def init_supabase_client():
    """Inicializa e retorna o cliente Supabase."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar com o Supabase: {e}")
        st.warning("Verifique se as configurações [supabase] estão corretas no seu secrets.toml.")
        return None

supabase: Client = init_supabase_client()

# --- Funções de Dados ---
def initialize_session_state():
    """Carrega os dados do Supabase para o session_state."""
    if 'dados' not in st.session_state:
        st.session_state['dados'] = load_data_from_db()

    os.makedirs(PLAYER_PHOTOS_DIR, exist_ok=True)
    os.makedirs(SUMULA_LEGACY_DIR, exist_ok=True)

def load_data_from_db():
    """Carrega todos os dados do Supabase."""
    if not supabase: return {'players': [], 'monthly_payments': {}}

    try:
        # Carrega jogadores
        players_response = supabase.table('players').select('*').execute()
        players_data = players_response.data

        # Carrega pagamentos
        payments_response = supabase.table('monthly_payments').select('*').execute()
        payments_data = payments_response.data

        # Formata os pagamentos no formato antigo para compatibilidade
        monthly_payments = {}
        for p in payments_data:
            year_str = str(p['year'])
            month_str = str(p['month'])
            player_name = p['player_name'] # Usando nome como chave, como antes

            if year_str not in monthly_payments:
                monthly_payments[year_str] = {}
            if player_name not in monthly_payments[year_str]:
                monthly_payments[year_str][player_name] = {}
            monthly_payments[year_str][player_name][month_str] = p['status']

        st.toast("Dados carregados do banco de dados.", icon="☁️")
        return {'players': players_data, 'monthly_payments': monthly_payments}

    except Exception as e:
        st.error(f"Erro ao carregar dados do banco de dados: {e}")
        return {'players': [], 'monthly_payments': {}}

def save_data():
    """Salva as alterações no Supabase."""
    if not supabase or 'dados' not in st.session_state:
        return

    try:
        # Salvar Jogadores (Upsert: atualiza se existe, insere se não)
        players_to_save = st.session_state.dados['players']
        if players_to_save:
            supabase.table('players').upsert(players_to_save).execute()

        # Salvar Pagamentos (Abordagem de deletar e recriar para simplicidade)
        # Primeiro, deleta todos os pagamentos existentes para os jogadores atuais
        all_player_names = [p['name'] for p in st.session_state.dados['players']]
        if all_player_names:
            supabase.table('monthly_payments').delete().in_('player_name', all_player_names).execute()

        # Depois, insere os novos dados de pagamento
        payments_to_insert = []
        payments_data = st.session_state.dados.get('monthly_payments', {})
        for year, players in payments_data.items():
            for player_name, months in players.items():
                for month, status in months.items():
                    payments_to_insert.append({
                        'player_name': player_name,
                        'year': int(year),
                        'month': int(month),
                        'status': status
                    })

        if payments_to_insert:
            supabase.table('monthly_payments').insert(payments_to_insert).execute()

        st.toast("✅ Dados salvos no banco de dados com sucesso!", icon="💾")
    except Exception as e:
        st.error(f"Erro ao salvar dados no banco de dados: {e}")


# --- Funções Auxiliares (adaptadas) ---
def get_players_df():
    if 'dados' in st.session_state and st.session_state['dados']['players']:
        return pd.DataFrame(st.session_state['dados']['players'])
    return pd.DataFrame()

# O resto das funções auxiliares (get_player_by_id, etc.) precisa ser adaptado
# para a nova estrutura de dados (sem 'id' de texto)
def get_player_by_name(player_name):
    for player in st.session_state.dados['players']:
        if player['name'] == player_name:
            return player
    return None
