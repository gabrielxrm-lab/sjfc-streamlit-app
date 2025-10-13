# pages/4_🎲_Sorteio_de_Times.py
import streamlit as st
import pandas as pd
import random
from collections import defaultdict
import data_manager

st.set_page_config(layout="wide", page_title="Sorteio de Times")
data_manager.initialize_session_state()

st.title("🎲 Sorteio de Times (Milan vs Inter)")

if 'team_milan' not in st.session_state:
    st.session_state.team_milan = []
    st.session_state.team_inter = []


def perform_draw():
    available_players_by_position = defaultdict(list)
    for player in st.session_state.dados['players']:
        available_players_by_position[player.get('position', 'DESCONHECIDO').upper()].append(player)

    for position_list in available_players_by_position.values():
        random.shuffle(position_list)

    team_milan = []
    team_inter = []

    for pos, players_in_pos in available_players_by_position.items():
        mid_point = len(players_in_pos) // 2
        for i, player in enumerate(players_in_pos):
            # Lógica simples de divisão
            if len(team_milan) <= len(team_inter):
                team_milan.append(player)
            else:
                team_inter.append(player)

    st.session_state.team_milan = sorted(team_milan, key=lambda p: p['name'])
    st.session_state.team_inter = sorted(team_inter, key=lambda p: p['name'])

def clear_draw():
    st.session_state.team_milan = []
    st.session_state.team_inter = []

# --- Controles ---
c1, c2, c3 = st.columns([2, 2, 8])
c1.button("⚡ Sortear Times!", on_click=perform_draw, type="primary", use_container_width=True)
c2.button("🧹 Limpar Sorteio", on_click=clear_draw, use_container_width=True)

st.write("---")

# --- Exibição dos Times ---
col_milan, col_inter = st.columns(2)

with col_milan:
    st.header("🔴 Milan")
    if st.session_state.team_milan:
        df_milan = pd.DataFrame(st.session_state.team_milan)[['name', 'position']]
        st.dataframe(df_milan, hide_index=True, use_container_width=True)
        st.subheader(f"Total: {len(st.session_state.team_milan)} jogadores")
    else:
        st.info("Time vazio.")

with col_inter:
    st.header("🔵 Inter de Milão")
    if st.session_state.team_inter:
        df_inter = pd.DataFrame(st.session_state.team_inter)[['name', 'position']]
        st.dataframe(df_inter, hide_index=True, use_container_width=True)
        st.subheader(f"Total: {len(st.session_state.team_inter)} jogadores")
    else:
        st.info("Time vazio.")