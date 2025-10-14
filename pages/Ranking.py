# pages/5_🏆_Ranking.py
import streamlit as st
import pandas as pd
import data_manager

st.set_page_config(layout="wide", page_title="Ranking Geral")
if 'dados' not in st.session_state:
    data_manager.initialize_session_state()

st.title("🏆 Ranking Geral de Atletas")
st.info("As estatísticas são atualizadas sempre que uma nova súmula é salva.")

game_stats = st.session_state.dados.get('game_stats', [])

if not game_stats:
    st.warning("Nenhuma estatística de jogo foi salva ainda. Salve uma súmula para começar.")
else:
    df = pd.DataFrame(game_stats)
    ranking = df.groupby('player_name').agg(
        Gols=('goals', 'sum'), Amarelos=('yellow_cards', 'sum'), Vermelhos=('red_cards', 'sum'),
        Craque_do_Jogo=('craque_do_jogo', lambda x: x.sum()),
        Goleiro_do_Jogo=('goleiro_do_jogo', lambda x: x.sum()),
        Gol_do_Jogo=('gol_do_jogo', lambda x: x.sum())
    ).reset_index().rename(columns={'player_name': 'Jogador'})
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚽ Artilharia")
        artilharia_df = ranking[['Jogador', 'Gols']].sort_values(by='Gols', ascending=False).reset_index(drop=True)
        artilharia_df.index += 1
        st.dataframe(artilharia_df[artilharia_df['Gols'] > 0], use_container_width=True)
    with col2:
        st.subheader("🟨 Cartões Amarelos")
        amarelos_df = ranking[['Jogador', 'Amarelos']].sort_values(by='Amarelos', ascending=False).reset_index(drop=True)
        amarelos_df.index += 1
        st.dataframe(amarelos_df[amarelos_df['Amarelos'] > 0], use_container_width=True)
    st.write("---")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🟥 Cartões Vermelhos")
        vermelhos_df = ranking[['Jogador', 'Vermelhos']].sort_values(by='Vermelhos', ascending=False).reset_index(drop=True)
        vermelhos_df.index += 1
        st.dataframe(vermelhos_df[vermelhos_df['Vermelhos'] > 0], use_container_width=True)
    with col4:
        st.subheader("⭐ Prêmios Individuais")
        premios_df = ranking[['Jogador', 'Craque_do_Jogo', 'Goleiro_do_Jogo', 'Gol_do_Jogo']]
        premios_df = premios_df[ (premios_df['Craque_do_Jogo'] > 0) | (premios_df['Goleiro_do_Jogo'] > 0) | (premios_df['Gol_do_Jogo'] > 0) ].sort_values(by='Craque_do_Jogo', ascending=False).reset_index(drop=True)
        premios_df.index += 1
        st.dataframe(premios_df, use_container_width=True)
