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
    # Garante que os times estejam limpos antes do sorteio
    st.session_state.team_milan = []
    st.session_state.team_inter = []
    
    available_players_by_position = defaultdict(list)
    for player in st.session_state.dados['players']:
        available_players_by_position[player.get('position', 'DESCONHECIDO').upper()].append(player)

    # Sorteia por posição para equilibrar
    for position, players in available_players_by_position.items():
        random.shuffle(players)
        for i, player in enumerate(players):
            if i % 2 == 0:
                st.session_state.team_milan.append(player)
            else:
                st.session_state.team_inter.append(player)

def clear_draw():
    st.session_state.team_milan = []
    st.session_state.team_inter = []

c1, c2, _ = st.columns([2, 2, 8])
c1.button("⚡ Sortear Times!", on_click=perform_draw, type="primary", use_container_width=True)
c2.button("🧹 Limpar Sorteio", on_click=clear_draw, use_container_width=True)

st.write("---")

col_milan, col_inter = st.columns(2)
with col_milan:
    st.header(f"🔴 Milan ({len(st.session_state.team_milan)})")
    if st.session_state.team_milan:
        df_milan = pd.DataFrame(sorted(st.session_state.team_milan, key=lambda p: p['name']))[['name', 'position']]
        st.dataframe(df_milan, hide_index=True, use_container_width=True)
    else:
        st.info("Time vazio.")

with col_inter:
    st.header(f"🔵 Inter ({len(st.session_state.team_inter)})")
    if st.session_state.team_inter:
        df_inter = pd.DataFrame(sorted(st.session_state.team_inter, key=lambda p: p['name']))[['name', 'position']]
        st.dataframe(df_inter, hide_index=True, use_container_width=True)
    else:
        st.info("Time vazio.")
