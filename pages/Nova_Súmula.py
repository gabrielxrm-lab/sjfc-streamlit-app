# pages/3_📋_Nova_Súmula.py
import streamlit as st
import data_manager
import datetime as dt
import os
import io
from collections import defaultdict

try:
    from reportlab.plat-yous import SimpleDocTemplate, Preformatted; from reportlab.lib.pagesizes import A4; from reportlab.lib.styles import getSampleStyleSheet; from reportlab.lib.units import cm; REPORTLAB_AVAILABLE = True
except ImportError: REPORTLAB_AVAILABLE = False

IS_DIRETORIA = st.session_state.get('role') == 'Diretoria'
st.set_page_config(layout="wide", page_title="Nova Súmula")
if 'dados' not in st.session_state: data_manager.initialize_session_state()
if 'sumula_data' not in st.session_state: st.session_state.sumula_data = {}

def limpar_sumula(): st.session_state.sumula_data.clear()

def montar_sumula_texto(dados_jogo):
    sd = st.session_state.sumula_data; placar_home = sum(sd.get('goals_home', {}).values()); placar_away = sum(sd.get('goals_away', {}).values())
    def formatar_gols(gdict):
        if not gdict: return "(Sem gols)"; gdict_tuples = {tuple(k) if isinstance(k, list) else k: v for k, v in gdict.items()}; sorted_goals = sorted(gdict_tuples.items(), key=lambda item: item[0][1]); return "\n".join([f"{n} ({c}) →{'⚽' * v} ({v})" for (n, c), v in sorted_goals])
    sumula_partes = [f"📋 SÚMULA: {dados_jogo.get('rodada', '')}", f"📅 {dados_jogo.get('dia', '')}, {dados_jogo.get('data', '')}", "", f"🏟 {dados_jogo.get('home_name', 'Casa')} {placar_home} x {placar_away} {dados_jogo.get('away_name', 'Visitante')}", "", f"⚽ GOL DO JOGO → {dados_jogo.get('gol_do_jogo', '(Não preenchido)')}", f"🧤 GOLEIRO DO JOGO → {dados_jogo.get('goleiro_do_jogo', '(Não preenchido)')}", f"⭐ CRAQUE DO JOGO → {dados_jogo.get('craque_do_jogo', '(Não preenchido)')}", "", "________________________________________", f"🔴⚫ Gols do {dados_jogo.get('home_name', 'Casa')}:", "", formatar_gols(sd.get('goals_home', {})), "", f"🟦⬛ Gols do {dados_jogo.get('away_name', 'Visitante')}:", "", formatar_gols(sd.get('goals_away', {})), "________________________________________", "", f"🟨 Cartões Amarelos – {dados_jogo.get('data', '')}", ""]
    amarelos = [f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in sd.get('yellow_cards_home', [])] + [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in sd.get('yellow_cards_away', [])]; sumula_partes.append("\n".join(amarelos) or "(Sem cartões amarelos)")
    sumula_partes.extend(["", f"🟥 Cartões Vermelhos – {dados_jogo.get('data', '')}", "", "\n".join([f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in sd.get('red_cards_home', [])] + [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in sd.get('red_cards_away', [])]) or "(Sem cartões vermelhos)", "________________________________________", "", "📌 Faltas não justificadas:", "", "\n".join(sd.get('faltas_nao', [])) or "(Nenhum)", "", "🚫 Suspensos:", "", "\n".join(sd.get('suspensos', [])) or "(Nenhum)", "________________________________________", "", "✅ Faltas justificadas:", "", "\n".join(f"({n})" for n in sd.get('faltas_sim', [])) or "(Nenhum)", "________________________________________", "", "🚑 Depto. Médico:", "", "\n".join(f"({n})" for n in sd.get('medico', [])) or "(Nenhum)", "________________________________________", "", "📆 Cumpriu suspensão:", "", "\n".join(f"{n} (APTO)" for n in sd.get('cumpriu_suspensao', [])) or "(Nenhum)", "________________________________________", "", "🟨 Cartões (Mês):", "", "\n".join(sd.get('cartoes_mes', [])) or "(Nenhum)"])
    sumula_partes.append(f"\n\n🖋 Gerado em: {dt.datetime.now(dt.timezone(dt.timedelta(hours=-3))).strftime('%d/%m/%Y %H:%M:%S')}"); return "\n".join(sumula_partes)

def save_stats_and_download_sumula():
    sd = st.session_state.sumula_data; stats_by_player = defaultdict(lambda: {'goals': 0, 'yellow_cards': 0, 'red_cards': 0, 'craque_do_jogo': False, 'goleiro_do_jogo': False, 'gol_do_jogo': False})
    for (player_name, _), goals in sd.get('goals_home', {}).items(): stats_by_player[player_name]['goals'] += goals
    for (player_name, _), goals in sd.get('goals_away', {}).items(): stats_by_player[player_name]['goals'] += goals
    for player_name in sd.get('yellow_cards_home', []) + sd.get('yellow_cards_away', []): stats_by_player[player_name]['yellow_cards'] += 1
    for player_name in sd.get('red_cards_home', []) + sd.get('red_cards_away', []): stats_by_player[player_name]['red_cards'] += 1
    if st.session_state.get('craque_jogo'): stats_by_player[st.session_state.craque_jogo]['craque_do_jogo'] = True
    if st.session_state.get('goleiro_jogo'): stats_by_player[st.session_state.goleiro_jogo]['goleiro_do_jogo'] = True
    if st.session_state.get('gol_jogo'): stats_by_player[st.session_state.gol_jogo]['gol_do_jogo'] = True
    final_stats_list = []; game_date_str = st.session_state.data_jogo.strftime("%Y-%m-%d")
    for player_name, stats in stats_by_player.items(): final_stats_list.append({'game_date': game_date_str, 'player_name': player_name, **stats})
    if final_stats_list: data_manager.save_game_stats_to_db(final_stats_list)
    limpar_sumula()

st.title("📋 Gerador de Súmula")
if not IS_DIRETORIA: st.warning("🔒 Apenas a Diretoria pode criar ou editar súmulas.")
if st.button("🗑️ Limpar Campos da Súmula", type="secondary", on_click=limpar_sumula, disabled=not IS_DIRETORIA): st.toast("Campos da súmula foram limpos.")
with st.container(border=True):
    st.subheader("📅 Dados do Jogo e Destaques"); c1, c2, c3 = st.columns(3); data_jogo = c1.date_input("Data", format="DD/MM/YYYY", key="data_jogo", disabled=not IS_DIRETORIA); dia_semana = c2.text_input("Dia da Semana", value=data_jogo.strftime("%A"), disabled=not IS_DIRETORIA); rodada = c3.text_input("Rodada", disabled=not IS_DIRETORIA)
    gol_jogo = c1.text_input("Gol do Jogo", key="gol_jogo", disabled=not IS_DIRETORIA); goleiro_jogo = c2.text_input("Goleiro do Jogo", key="goleiro_jogo", disabled=not IS_DIRETORIA); craque_jogo = c3.text_input("Craque do Jogo", key="craque_jogo", disabled=not IS_DIRETORIA)

# --- CORREÇÃO AQUI ---
# A variável 'sd' precisa ser definida ANTES de ser usada.
col_home, col_away = st.columns(2)
sd = st.session_state.sumula_data

with col_home:
    with st.container(border=True):
        st.subheader("🔴 Time da Casa"); home_name = st.text_input("Nome", value="SÃO JORGE", key="home_name", disabled=not IS_DIRETORIA); home_score = sum(sd.get('goals_home', {}).values()); st.metric("Placar", home_score)
        with st.form("home_goal_form", clear_on_submit=True):
            st.markdown("**Adicionar Gol**"); nome, camisa, qtd = st.columns(3); nome_gol = nome.text_input("Jogador", key="h_g_n", label_visibility="collapsed", placeholder="Nome", disabled=not IS_DIRETORIA); camisa_gol = camisa.number_input("Camisa", min_value=1, step=1, key="h_g_c", label_visibility="collapsed", disabled=not IS_DIRETORIA); qtd_gol = qtd.number_input("Qtd", min_value=1, step=1, value=1, key="h_g_q", label_visibility="collapsed", disabled=not IS_DIRETORIA)
            if st.form_submit_button("➕ Adicionar Gol", disabled=not IS_DIRETORIA):
                if nome_gol and camisa_gol > 0: chave = (nome_gol, int(camisa_gol)); sd.setdefault('goals_home', {}); sd['goals_home'][chave] = sd['goals_home'].get(chave, 0) + qtd_gol
        st.write("**Gols Registrados:**")
        for (nome, camisa), qtd in list(sd.get('goals_home', {}).items()):
            c1, c2 = st.columns([4, 1]); c1.text(f"⚽ {nome} ({camisa}) - {qtd} gol(s)");
            if c2.button("🗑️", key=f"del_hg_{nome}_{camisa}", use_container_width=True, disabled=not IS_DIRETORIA): del sd['goals_home'][(nome, camisa)]; st.rerun()
        st.write("---")
        with st.form("home_card_form", clear_on_submit=True):
            st.markdown("**Adicionar Cartão**"); nome_cartao = st.text_input("Jogador", key="h_c_n", label_visibility="collapsed", placeholder="Nome", disabled=not IS_DIRETORIA); c1, c2 = st.columns(2)
            if c1.form_submit_button("🟨 Amarelo", use_container_width=True, disabled=not IS_DIRETORIA):
                if nome_cartao: sd.setdefault('yellow_cards_home', []).append(nome_cartao)
            if c2.form_submit_button("🟥 Vermelho", use_container_width=True, disabled=not IS_DIRETORIA):
                if nome_cartao: sd.setdefault('red_cards_home', []).append(nome_cartao)
        st.write("**Cartões Registrados:**")
        for i, nome in enumerate(list(sd.get('yellow_cards_home', []))):
            c1, c2 = st.columns([4, 1]); c1.text(f"🟨 {nome}");
            if c2.button("🗑️", key=f"del_hy_{nome}_{i}", use_container_width=True, disabled=not IS_DIRETORIA): sd['yellow_cards_home'].pop(i); st.rerun()
        for i, nome in enumerate(list(sd.get('red_cards_home', []))):
            c1, c2 = st.columns([4, 1]); c1.text(f"🟥 {nome}");
            if c2.button("🗑️", key=f"del_hr_{nome}_{i}", use_container_width=True, disabled=not IS_DIRETORIA): sd['red_cards_home'].pop(i); st.rerun()

with col_away:
    with st.container(border=True):
        st.subheader("🟦 Time Visitante"); away_name = st.text_input("Nome", value="ADVERSÁRIO", key="away_name", disabled=not IS_DIRETORIA); away_score = sum(sd.get('goals_away', {}).values()); st.metric("Placar", away_score)
        with st.form("away_goal_form", clear_on_submit=True):
            st.markdown("**Adicionar Gol**"); nome, camisa, qtd = st.columns(3); nome_gol = nome.text_input("Jogador", key="a_g_n", label_visibility="collapsed", placeholder="Nome", disabled=not IS_DIRETORIA); camisa_gol = camisa.number_input("Camisa", min_value=1, step=1, key="a_g_c", label_visibility="collapsed", disabled=not IS_DIRETORIA); qtd_gol = qtd.number_input("Qtd", min_value=1, step=1, value=1, key="a_g_q", label_visibility="collapsed", disabled=not IS_DIRETORIA)
            if st.form_submit_button("➕ Adicionar Gol", disabled=not IS_DIRETORIA):
                if nome_gol and camisa_gol > 0: chave = (nome_gol, int(camisa_gol)); sd.setdefault('goals_away', {}); sd['goals_away'][chave] = sd['goals_away'].get(chave, 0) + qtd_gol
        st.write("**Gols Registrados:**")
        for (nome, camisa), qtd in list(sd.get('goals_away', {}).items()):
            c1, c2 = st.columns([4, 1]); c1.text(f"⚽ {nome} ({camisa}) - {qtd} gol(s)");
            if c2.button("🗑️", key=f"del_ag_{nome}_{camisa}", use_container_width=True, disabled=not IS_DIRETORIA): del sd['goals_away'][(nome, camisa)]; st.rerun()
        st.write("---")
        with st.form("away_card_form", clear_on_submit=True):
            st.markdown("**Adicionar Cartão**"); nome_cartao = st.text_input("Jogador", key="a_c_n", label_visibility="collapsed", placeholder="Nome", disabled=not IS_DIRETORIA); c1, c2 = st.columns(2)
            if c1.form_submit_button("🟨 Amarelo", use_container_width=True, disabled=not IS_DIRETORIA):
                if nome_cartao: sd.setdefault('yellow_cards_away', []).append(nome_cartao)
            if c2.form_submit_button("🟥 Vermelho", use_container_width=True, disabled=not IS_DIRETORIA):
                if nome_cartao: sd.setdefault('red_cards_away', []).append(nome_cartao)
        st.write("**Cartões Registrados:**")
        for i, nome in enumerate(list(sd.get('yellow_cards_away', []))):
            c1, c2 = st.columns([4, 1]); c1.text(f"🟨 {nome}");
            if c2.button("🗑️", key=f"del_ay_{nome}_{i}", use_container_width=True, disabled=not IS_DIRETORIA): sd['yellow_cards_away'].pop(i); st.rerun()
        for i, nome in enumerate(list(sd.get('red_cards_away', []))):
            c1, c2 = st.columns([4, 1]); c1.text(f"🟥 {nome}");
            if c2.button("🗑️", key=f"del_ar_{nome}_{i}", use_container_width=True, disabled=not IS_DIRETORIA): sd['red_cards_away'].pop(i); st.rerun()

st.write("---"); st.header("📌 Ocorrências Gerais")
def create_occurrence_section(title, key, placeholder):
    with st.container(border=True):
        st.subheader(title)
        with st.form(f"form_{key}", clear_on_submit=True):
            new_item = st.text_input("Adicionar nome:", key=f"add_{key}", placeholder=placeholder, label_visibility="collapsed", disabled=not IS_DIRETORIA)
            if st.form_submit_button(f"➕ Adicionar a {title}", disabled=not IS_DIRETORIA):
                if new_item: sd.setdefault(key, []).append(new_item)
        st.write("**Lista Atual:**");
        if not sd.get(key): st.caption("Vazia")
        for i, item in enumerate(list(sd.get(key, []))):
            c1, c2 = st.columns([4, 1]); c1.text(item);
            if c2.button("🗑️", key=f"del_{key}_{i}", use_container_width=True, disabled=not IS_DIRETORIA): sd[key].pop(i); st.rerun()
c1, c2, c3 = st.columns(3)
with c1: create_occurrence_section("🚫 Suspensos", "suspensos", "Nome do jogador"); create_occurrence_section("📌 Faltas não justificadas", "faltas_nao", "Nome do jogador")
with c2: create_occurrence_section("📆 Cumpriu Suspensão", "cumpriu_suspensao", "Nome do jogador"); create_occurrence_section("✅ Faltas justificadas", "faltas_sim", "Nome (motivo)")
with c3: create_occurrence_section("🚑 Departamento Médico", "medico", "Nome (lesão)"); create_occurrence_section("🟨 Cartões (Mês)", "cartoes_mes", "Nome (2 amarelos)")
st.write("---")
with st.container(border=True):
    st.header("📄 Prévia e Download da Súmula"); dados_jogo_dict = {'data': data_jogo.strftime("%d-%m-%Y"), 'dia': dia_semana, 'rodada': rodada, 'gol_do_jogo': gol_jogo, 'goleiro_do_jogo': goleiro_jogo, 'craque_do_jogo': craque_jogo, 'home_name': home_name, 'away_name': away_name}; sumula_final = montar_sumula_texto(dados_jogo_dict)
    st.code(sumula_final, height=400); nome_base_arquivo = f"sumula_{data_jogo.strftime('%d-%m-%Y')}"; c1, c2 = st.columns(2)
    if c1.button("Salvar Estatísticas e Baixar TXT", use_container_width=True, type="primary", on_click=save_stats_and_download_sumula, disabled=not IS_DIRETORIA):
        st.download_button(label="Clique aqui para baixar o TXT", data=sumula_final.encode('utf-8'), file_name=f"{nome_base_arquivo}.txt", mime="text/plain")
    if REPORTLAB_AVAILABLE and c2.button("Salvar Estatísticas e Baixar PDF", use_container_width=True, on_click=save_stats_and_download_sumula, disabled=not IS_DIRETORIA):
        buffer = io.BytesIO(); doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm); story = [Preformatted(sumula_final, getSampleStyleSheet()["Code"])]; doc.build(story); pdf_bytes = buffer.getvalue()
        st.download_button(label="Clique aqui para baixar o PDF", data=pdf_bytes, file_name=f"{nome_base_arquivo}.pdf", mime="application/pdf")
