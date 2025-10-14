# data_manager.py
import streamlit as st
import os
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import io
import requests

# --- Configurações ---
PLAYER_PHOTOS_DIR = 'player_photos'
SUMULA_LEGACY_DIR = 'sumulas'
SUPABASE_BUCKET_NAME = "arquivos_sjfc"
GITHUB_USER = "gabrielxrm-lab" 
GITHUB_REPO = "sjfc-streamlit-app"
FOTOS_PATH = "player_photos"

# --- Conexão com Supabase ---
@st.cache_resource
def init_supabase_client():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception:
        st.error("Falha na conexão com o Supabase. Verifique suas chaves em 'Secrets'.")
        return None

supabase: Client = init_supabase_client()

# --- Funções de Storage do GitHub ---
@st.cache_data(ttl=300)
def get_photo_list_from_github():
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FOTOS_PATH}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()
        photo_names = [file['name'] for file in files if file['type'] == 'file' and not file['name'].endswith('.txt')]
        return ["Nenhuma"] + sorted(photo_names)
    except Exception as e:
        st.error(f"Não foi possível buscar as fotos do GitHub. Erro: {e}")
        return ["Nenhuma"]

def get_github_image_url(filename):
    if not filename or filename == "Nenhuma":
        return "https://via.placeholder.com/200x200.png?text=Sem+Foto"
    return f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{FOTOS_PATH}/{filename}"

# --- Funções de Dados ---
def initialize_session_state():
    if 'dados' not in st.session_state: st.session_state['dados'] = load_data_from_db()
    os.makedirs(PLAYER_PHOTOS_DIR, exist_ok=True); os.makedirs(SUMULA_LEGACY_DIR, exist_ok=True)

def load_data_from_db():
    if not supabase: return {'players': [], 'monthly_payments': {}, 'game_stats': []}
    try:
        players_data = supabase.table('Players').select('*').order('name').execute().data
        payments_data = supabase.table('monthly_payments').select('*').execute().data
        stats_data = supabase.table('game_stats').select('*').execute().data
        monthly_payments_structured = {}
        for p in payments_data:
            year_str, month_str, player_id_str = str(p['year']), str(p['month']), str(p['player_id'])
            if year_str not in monthly_payments_structured: monthly_payments_structured[year_str] = {}
            if player_id_str not in monthly_payments_structured[year_str]: monthly_payments_structured[year_str][player_id_str] = {}
            monthly_payments_structured[year_str][player_id_str][month_str] = p['status']
        st.toast("Dados carregados da nuvem.", icon="☁️")
        return {'players': players_data, 'monthly_payments': monthly_payments_structured, 'game_stats': stats_data}
    except Exception as e:
        st.error(f"Erro ao carregar dados do Supabase: {e}"); return {'players': [], 'monthly_payments': {}, 'game_stats': []}

def save_data_to_db():
    if not supabase or 'dados' not in st.session_state: st.error("Cliente Supabase não inicializado."); return
    try:
        players_to_save = st.session_state.dados.get('players', [])
        if players_to_save:
            # --- CORREÇÃO APLICADA AQUI ---
            # Prepara uma lista "limpa" para o upsert.
            upsert_list = []
            for player in players_to_save:
                # Se o jogador não tem um ID válido, é novo.
                if not player.get('id'):
                    # Cria uma cópia do jogador e remove a chave 'id' se ela existir
                    new_player = player.copy()
                    new_player.pop('id', None) 
                    upsert_list.append(new_player)
                else:
                    # Se o jogador já tem ID, apenas o adiciona à lista.
                    upsert_list.append(player)
            
            if upsert_list:
                supabase.table('Players').upsert(upsert_list).execute()

        payments_to_insert = []
        # Usa a lista de jogadores recarregada para garantir que temos todos os IDs
        reloaded_players = supabase.table('Players').select('id').execute().data
        player_ids_in_app = [p['id'] for p in reloaded_players]
        
        if player_ids_in_app:
            supabase.table('monthly_payments').delete().in_('player_id', player_ids_in_app).execute()
            payments_data = st.session_state.dados.get('monthly_payments', {})
            for year, players in payments_data.items():
                for player_id, months in players.items():
                    if int(player_id) in player_ids_in_app:
                        for month, status in months.items():
                            payments_to_insert.append({'player_id': int(player_id), 'year': int(year), 'month': int(month), 'status': status})
            if payments_to_insert: supabase.table('monthly_payments').insert(payments_to_insert).execute()
        
        st.success("✅ Dados salvos na nuvem!")
        st.session_state['dados'] = load_data_from_db(); st.rerun()

    except Exception as e: st.error(f"Erro ao salvar dados no Supabase: {e}")

def save_game_stats_to_db(stats_list):
    if not supabase or not stats_list: return
    try:
        supabase.table('game_stats').insert(stats_list).execute(); st.success("📊 Estatísticas da partida salvas com sucesso!")
        st.session_state['dados']['game_stats'].extend(stats_list)
    except Exception as e: st.error(f"Erro ao salvar estatísticas da partida: {e}")

def delete_players_by_ids(ids_to_delete):
    if not supabase or not ids_to_delete: return
    try:
        supabase.table('Players').delete().in_('id', ids_to_delete).execute(); st.toast(f"{len(ids_to_delete)} jogador(es) removido(s) do banco de dados.")
    except Exception as e: st.error(f"Erro ao deletar jogadores: {e}")

def get_players_df():
    players = st.session_state.dados.get('players', []); return pd.DataFrame(players) if players else pd.DataFrame()

def get_player_name_by_id(player_id):
    player_id = int(player_id)
    for player in st.session_state.dados.get('players', []):
        if player['id'] == player_id: return player['name']
    return "Jogador não encontrado"
