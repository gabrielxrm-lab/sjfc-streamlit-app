# pages/3_📋_Nova_Súmula.py
import streamlit as st
import data_manager
import datetime as dt
import os
import io
from collections import defaultdict

try:
    from reportlab.platypus import SimpleDocTemplate, Preformatted; from reportlab.lib.pagesizes import A4; from reportlab.lib.styles import getSampleStyleSheet; from reportlab.lib.units import cm; REPORTLAB_AVAILABLE = True
except ImportError: REPORTLAB_AVAILABLE = False

IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'
st.set_page_config(layout="wide", page_title="Nova Súmula")
if 'dados' not in st.session_state: data_manager.initialize_session_state()
if 'sumula_data' not in st.session_state: st.session_state.sumula_data = {}

def limpar_sumula(): st.session_state.sumula_data.clear()

def montar_sumula_texto(dados_jogo):
    sd = st.session_state.sumula_data
    placar_home = sum(sd.get('goals_home', {}).values()); placar_away = sum(sd.get('goals_away', {}).values())
    def formatar_gols(gdict):
        if not gdict: return "(Sem gols)"; gdict_tuples = {tuple(k) if isinstance(k, list) else k: v for k, v in gdict.items()}; sorted_goals = sorted(gdict_tuples.items(), key=lambda item: item[0][1]); return "\n".join([f"{n} ({c}) →{'⚽' * v} ({v})" for (n, c), v in sorted_goals])
    
    # Atualiza a exibição dos prêmios para suportar múltiplos nomes
    craques = ", ".join(sd.get('craques_do_jogo', [])) or "(Não preenchido)"
    goleiros = ", ".join(sd.get('goleiros_do_jogo', [])) or "(Não preenchido)"
    gols = ", ".join(sd.get('gols_do_jogo', [])) or "(Não preenchido)"

    sumula_partes = [
        f"📋 SÚMULA: {dados_jogo.get('rodada', '')}", f"📅 {dados_jogo.get('dia', '')}, {dados_jogo.get('data', '')}", "",
        f"🏟 {dados_jogo.get('home_name', 'Casa')} {placar_home} x {placar_away} {dados_jogo.get('away_name', 'Visitante')}", "",
        f"⚽ GOL(S) DO JOGO → {gols}", f"🧤 GOLEIRO(S) DO JOGO → {goleiros}", f"⭐ CRAQUE(S) DO JOGO → {craques}",
        "", "________________________________________",
        # ... (O resto da função permanece igual)
    ]
    # ... (código restante da função omitido para encurtar)
    amarelos = [f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in sd.get('yellow_cards_home', [])] + [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in sd.get('yellow_cards_away', [])]; sumula_partes.append(f"🔴⚫ Gols do {dados_jogo.get('home_name', 'Casa')}:\n\n{formatar_gols(sd.get('goals_home', {}))}\n\n🟦⬛ Gols do {dados_jogo.get('away_name', 'Visitante')}:\n\n{formatar_gols(sd.get('goals_away', {}))}\n________________________________________\n\n🟨 Cartões Amarelos – {dados_jogo.get('data', '')}\n\n" + ("\n".join(amarelos) or "(Sem cartões amarelos)"))
    sumula_partes.extend(["", f"🟥 Cartões Vermelhos – {dados_jogo.get('data', '')}", "", "\n".join([f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in sd.get('red_cards_home', [])] + [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in sd.get('red_cards_away', [])]) or "(Sem cartões vermelhos)", "________________________________________", "", "📌 Faltas não justificadas:", "", "\n".join(sd.get('faltas_nao', [])) or "(Nenhum)", "", "🚫 Suspensos:", "", "\n".join(sd.get('suspensos', [])) or "(Nenhum)", "________________________________________", "", "✅ Faltas justificadas:", "", "\n".join(f"({n})" for n in sd.get('faltas_sim', [])) or "(Nenhum)", "________________________________________", "", "🚑 Depto. Médico:", "", "\n".join(f"({n})" for n in sd.get('medico', [])) or "(Nenhum)", "________________________________________", "", "📆 Cumpriu suspensão:", "", "\n".join(f"{n} (APTO)" for n in sd.get('cumpriu_suspensao', [])) or "(Nenhum)", "________________________________________", "", "🟨 Cartões (Mês):", "", "\n".join(sd.get('cartoes_mes', [])) or "(Nenhum)"])
    sumula_partes.append(f"\n\n🖋 Gerado em: {dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S')}"); return "\n".join(sumula_partes)

def save_stats_and_download_sumula():
    sd = st.session_state.sumula_data; stats_by_player = defaultdict(lambda: {'goals': 0, 'yellow_cards': 0, 'red_cards': 0, 'craque_do_jogo': False, 'goleiro_do_jogo': False, 'gol_do_jogo': False})
    for (player_name, _), goals in sd.get('goals_home', {}).items(): stats_by_player[player_name]['goals'] += goals
    for (player_name, _), goals in sd.get('goals_away', {}).items(): stats_by_player[player_name]['goals'] += goals
    for player_name in sd.get('yellow_cards_home', []) + sd.get('yellow_cards_away', []): stats_by_player[player_name]['yellow_cards'] += 1
    for player_name in sd.get('red_cards_home', []) + sd.get('red_cards_away', []): stats_by_player[player_name]['red_cards'] += 1
    
    # Atualiza a coleta de prêmios para iterar sobre as listas
    for player_name in sd.get('craques_do_jogo', []): stats_by_player[player_name]['craque_do_jogo'] = True
    for player_name in sd.get('goleiros_do_jogo', []): stats_by_player[player_name]['goleiro_do_jogo'] = True
    for player_name in sd.get('gols_do_jogo', []): stats_by_player[player_name]['gol_do_jogo'] = True

    final_stats_list = []; game_date_str = st.session_state.data_jogo.strftime("%Y-%m-%d")
    for player_name, stats in stats_by_player.items(): final_stats_list.append({'game_date': game_date_str, 'player_name': player_name, **stats})
    if final_stats_list: data_manager.save_game_stats_to_db(final_stats_list)
    limpar_sumula()

# --- Interface do Usuário ---
st.title("📋 Gerador de Súmula")
if not IS_DIRETORIA: st.warning("🔒 Apenas a Diretoria pode criar ou editar súmulas.")
if st.button("🗑️ Limpar Campos da Súmula", type="secondary", on_click=limpar_sumula, disabled=not IS_DIRETORIA): st.toast("Campos da súmula foram limpos.")

with st.container(border=True):
    st.subheader("📅 Dados Gerais da Partida")
    c1, c2, c3 = st.columns(3)
    data_jogo = c1.date_input("Data", format="DD/MM/YYYY", key="data_jogo", disabled=not IS_DIRETORIA)
    dia_semana = c2.text_input("Dia da Semana", value=data_jogo.strftime("%A"), disabled=not IS_DIRETORIA)
    rodada = c3.text_input("Rodada", disabled=not IS_DIRETORIA)

# --- NOVA SEÇÃO DE DESTAQUES ---
st.header("🏆 Destaques Individuais")
def create_award_section(title, key, placeholder):
    with st.container(border=True):
        st.subheader(title)
        with st.form(f"form_award_{key}", clear_on_submit=True):
            new_item = st.text_input("Adicionar jogador:", key=f"add_award_{key}", placeholder=placeholder, label_visibility="collapsed")
            if st.form_submit_button(f"➕ Adicionar", disabled=not IS_DIRETORIA):
                if new_item: st.session_state.sumula_data.setdefault(key, []).append(new_item)
        
        st.write("**Premiados:**")
        if not st.session_state.sumula_data.get(key): st.caption("Nenhum")
        for i, item in enumerate(list(st.session_state.sumula_data.get(key, []))):
            c1, c2 = st.columns([4, 1])
            c1.text(item)
            if c2.button("🗑️", key=f"del_award_{key}_{i}", use_container_width=True, disabled=not IS_DIRETORIA):
                st.session_state.sumula_data[key].pop(i)
                st.rerun()

c1, c2, c3 = st.columns(3)
with c1:
    create_award_section("⭐ Craque(s) do Jogo", "craques_do_jogo", "Nome do craque")
with c2:
    create_award_section("🧤 Goleiro(s) do Jogo", "goleiros_do_jogo", "Nome do goleiro")
with c3:
    create_award_section("⚽ Gol(s) do Jogo", "gols_do_jogo", "Nome do autor do gol")

st.header("📝 Detalhes dos Times")
col_home, col_away = st.columns(2)
sd = st.session_state.sumula_data
# ... (o resto do código com as colunas dos times, ocorrências gerais e prévia permanece o mesmo)
# Omitido para encurtar
