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
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error("Falha na conexão com o Supabase. Verifique suas chaves em 'Secrets'.")
        return None

supabase: Client = init_supabase_client()

def initialize_session_state():
    if 'dados' not in st.session_state:
        st.session_state['dados'] = load_data_from_db()
    os.makedirs(PLAYER_PHOTOS_DIR, exist_ok=True)
    os.makedirs(SUMULA_LEGACY_DIR, exist_ok=True)

def load_data_from_db():
    if not supabase:
        return {'players': [], 'monthly_payments': {}}
    
    try:
        # ALTERAÇÃO AQUI: 'players' para 'Players'
        players_response = supabase.table('Players').select('*').order('name').execute()
        players_data = players_response.data

        # ALTERAÇÃO AQUI: 'monthly_payments' para 'monthly_payments' (verifique o seu)
        # Por padrão, vamos manter minúsculo, mas se o erro persistir para esta tabela, mude para 'Monthly_payments'
        payments_response = supabase.table('monthly_payments').select('*').execute()
        payments_data = payments_response.data
        
        monthly_payments_structured = {}
        for p in payments_data:
            year_str = str(p['year'])
            month_str = str(p['month'])
            player_id_str = str(p['player_id'])
            if year_str not in monthly_payments_structured:
                monthly_payments_structured[year_str] = {}
            if player_id_str not in monthly_payments_structured[year_str]:
                monthly_payments_structured[year_str][player_id_str] = {}
            monthly_payments_structured[year_str][player_id_str][month_str] = p['status']
        
        st.toast("Dados carregados da nuvem.", icon="☁️")
        return {'players': players_data, 'monthly_payments': monthly_payments_structured}
    
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {e}")
        return {'players': [], 'monthly_payments': {}}

def save_data_to_db():
    if not supabase or 'dados' not in st.session_state:
        st.error("Cliente Supabase não inicializado. Não é possível salvar.")
        return
    try:
        players_to_save = st.session_state.dados.get('players', [])
        if players_to_save:
            for player in players_to_save:
                if 'id' in player and player['id'] is None:
                    del player['id']
            # ALTERAÇÃO AQUI: 'players' para 'Players'
            supabase.table('Players').upsert(players_to_save).execute()

        payments_to_insert = []
        player_ids_in_app = [p['id'] for p in players_to_save if 'id' in p]
        if player_ids_in_app:
            # ALTERAÇÃO AQUI: Verifique o nome da sua tabela 'monthly_payments'
            supabase.table('monthly_payments').delete().in_('player_id', player_ids_in_app).execute()
            payments_data = st.session_state.dados.get('monthly_payments', {})
            for year, players in payments_data.items():
                for player_id, months in players.items():
                    if int(player_id) in player_ids_in_app:
                        for month, status in months.items():
                            payments_to_insert.append({
                                'player_id': int(player_id),
                                'year': int(year),
                                'month': int(month),
                                'status': status
                            })
            if payments_to_insert:
                # ALTERAÇÃO AQUI: Verifique o nome da sua tabela 'monthly_payments'
                supabase.table('monthly_payments').insert(payments_to_insert).execute()
        
        st.success("✅ Dados salvos na nuvem com sucesso!")
        st.session_state['dados'] = load_data_from_db()
        st.rerun()

    except Exception as e:
        st.error(f"Erro ao salvar dados no Supabase: {e}")

def delete_players_by_ids(ids_to_delete):
    if not supabase or not ids_to_delete:
        return
    try:
        # ALTERAÇÃO AQUI: 'players' para 'Players'
        supabase.table('Players').delete().in_('id', ids_to_delete).execute()
        st.toast(f"{len(ids_to_delete)} jogador(es) removido(s) do banco de dados.")
    except Exception as e:
        st.error(f"Erro ao deletar jogadores: {e}")

# --- Funções Auxiliares ---
def get_players_df():
    players = st.session_state.dados.get('players', [])
    return pd.DataFrame(players) if players else pd.DataFrame()

def get_player_name_by_id(player_id):
    player_id = int(player_id)
    for player in st.session_state.dados.get('players', []):
        if player['id'] == player_id:
            return player['name']
    return "Jogador não encontrado"
