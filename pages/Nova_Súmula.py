# pages/3_📋_Nova_Súmula.py
import streamlit as st
import data_manager
import datetime as dt
import re
from collections import defaultdict
import os

try:
    from reportlab.platypus import SimpleDocTemplate, Preformatted
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


st.set_page_config(layout="wide", page_title="Nova Súmula")
data_manager.initialize_session_state()

# --- Funções Utilitárias da Súmula Original ---
def gerar_bolinhas(qtd):
    try: qtd = int(qtd)
    except (ValueError, TypeError): return ""
    return " " + "⚽" * min(qtd, 12) if qtd > 0 else ""

# --- Inicialização do Estado da Súmula ---
if 'sumula_data' not in st.session_state:
    st.session_state.sumula_data = {
        'goals_home': {}, 'goals_away': {},
        'yellow_cards_home': [], 'yellow_cards_away': [],
        'red_cards_home': [], 'red_cards_away': [],
        'faltas_nao': [], 'faltas_sim': [], 'medico': [],
        'suspensos': [], 'cumpriu_suspensao': [], 'cartoes_mes': []
    }

def limpar_sumula():
    st.session_state.sumula_data = {
        'goals_home': {}, 'goals_away': {},
        'yellow_cards_home': [], 'yellow_cards_away': [],
        'red_cards_home': [], 'red_cards_away': [],
        'faltas_nao': [], 'faltas_sim': [], 'medico': [],
        'suspensos': [], 'cumpriu_suspensao': [], 'cartoes_mes': []
    }

def montar_sumula_texto(dados_jogo):
    placar_home = sum(st.session_state.sumula_data['goals_home'].values())
    placar_away = sum(st.session_state.sumula_data['goals_away'].values())

    def formatar_gols(gdict):
        if not gdict: return "(Sem gols)"
        gdict_tuples = {tuple(k) if isinstance(k, list) else k: v for k, v in gdict.items()}
        sorted_goals = sorted(gdict_tuples.items(), key=lambda item: item[0][1])
        return "\n".join([f"{n} ({c}) →{gerar_bolinhas(q)} ({q})" for (n, c), q in sorted_goals])

    sumula_partes = [
        f"📋 SÚMULA: {dados_jogo.get('rodada', '')}", f"📅 {dados_jogo.get('dia', '')}, {dados_jogo.get('data', '')}", "",
        f"🏟 {dados_jogo.get('home_name', 'Casa')} {placar_home} x {placar_away} {dados_jogo.get('away_name', 'Visitante')}", "",
        f"⚽ GOL DO JOGO → {dados_jogo.get('gol_do_jogo', '(Não preenchido)')}",
        f"🧤 GOLEIRO DO JOGO → {dados_jogo.get('goleiro_do_jogo', '(Não preenchido)')}",
        f"⭐ CRAQUE DO JOGO → {dados_jogo.get('craque_do_jogo', '(Não preenchido)')}", "", "________________________________________",
        f"🔴⚫ Gols do {dados_jogo.get('home_name', 'Casa')}:", "", formatar_gols(st.session_state.sumula_data['goals_home']), "",
        f"🟦⬛ Gols do {dados_jogo.get('away_name', 'Visitante')}:", "", formatar_gols(st.session_state.sumula_data['goals_away']),
        "________________________________________", "", f"🟨 Cartões Amarelos – {dados_jogo.get('data', '')}", ""
    ]
    amarelos = [f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in st.session_state.sumula_data['yellow_cards_home']] + \
               [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in st.session_state.sumula_data['yellow_cards_away']]
    sumula_partes.append("\n".join(amarelos) or "(Sem cartões amarelos)")

    sumula_partes.extend([
        "", f"🟥 Cartões Vermelhos – {dados_jogo.get('data', '')}", "",
        "\n".join([f"{n} ({dados_jogo.get('home_name', 'Casa')})" for n in st.session_state.sumula_data['red_cards_home']] +
                  [f"{n} ({dados_jogo.get('away_name', 'Visitante')})" for n in st.session_state.sumula_data['red_cards_away']]) or "(Sem cartões vermelhos)",
        "________________________________________", "", "📌 Faltas não justificadas:", "", "\n".join(st.session_state.sumula_data['faltas_nao']) or "(Nenhum)",
        "", "🚫 Suspensos:", "", "\n".join(st.session_state.sumula_data['suspensos']) or "(Nenhum)",
        "________________________________________", "", "✅ Faltas justificadas:", "", "\n".join(f"({n})" for n in st.session_state.sumula_data['faltas_sim']) or "(Nenhum)",
        "________________________________________", "", "🚑 Depto. Médico:", "", "\n".join(f"({n})" for n in st.session_state.sumula_data['medico']) or "(Nenhum)",
        "________________________________________", "", "📆 Cumpriu suspensão:", "", "\n".join(f"{n} (APTO)" for n in st.session_state.sumula_data['cumpriu_suspensao']) or "(Nenhum)",
        "________________________________________", "", "🟨 Cartões (Mês):", "", "\n".join(st.session_state.sumula_data['cartoes_mes']) or "(Nenhum)"
    ])

    sumula_partes.append(f"\n\n🖋 Gerado em: {dt.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return "\n".join(sumula_partes)

st.title("📋 Gerador de Súmula")

if st.button("🗑️ Limpar Todos os Campos", type="secondary"):
    limpar_sumula()
    st.rerun()

# --- Dados do Jogo ---
with st.container(border=True):
    st.subheader("📅 Dados do Jogo")
    c1, c2, c3 = st.columns(3)
    data_jogo = c1.date_input("Data do Jogo", format="DD/MM/YYYY")
    dia_semana = c2.text_input("Dia da Semana", value=data_jogo.strftime("%A"))
    rodada = c3.text_input("Rodada")

# --- Destaques ---
with st.container(border=True):
    st.subheader("🏆 Destaques da Partida")
    c1, c2, c3 = st.columns(3)
    gol_jogo = c1.text_input("Gol do Jogo")
    goleiro_jogo = c2.text_input("Goleiro do Jogo")
    craque_jogo = c3.text_input("Craque do Jogo")

# --- Times, Gols e Cartões ---
col_home, col_away = st.columns(2)
with col_home:
    with st.container(border=True):
        st.subheader("🔴 Time da Casa")
        home_name = st.text_input("Nome do Time da Casa", value="SÃO JORGE", key="home_name")
        home_score = sum(st.session_state.sumula_data['goals_home'].values())
        st.metric("Placar", home_score)
        
        with st.form("home_goal_form", clear_on_submit=True):
            st.markdown("**Adicionar Gol**")
            nome = st.text_input("Nome do Jogador (Gol)", key="h_g_n")
            camisa = st.number_input("Camisa (Gol)", min_value=1, max_value=99, step=1, key="h_g_c")
            qtd = st.number_input("Qtd. Gols", min_value=1, max_value=10, step=1, value=1, key="h_g_q")
            if st.form_submit_button("➕ Adicionar Gol"):
                chave = (nome, int(camisa))
                st.session_state.sumula_data['goals_home'][chave] = st.session_state.sumula_data['goals_home'].get(chave, 0) + qtd

        st.write("**Gols Registrados (Casa):**")
        for (nome, camisa), qtd in st.session_state.sumula_data['goals_home'].items():
            st.text(f"⚽ {nome} ({camisa}) - {qtd} gol(s)")
        
        st.write("---")
        with st.form("home_card_form", clear_on_submit=True):
            st.markdown("**Adicionar Cartão**")
            nome_cartao = st.text_input("Nome do Jogador (Cartão)", key="h_c_n")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("🟨 Amarelo", use_container_width=True):
                if nome_cartao and nome_cartao not in st.session_state.sumula_data['yellow_cards_home']: st.session_state.sumula_data['yellow_cards_home'].append(nome_cartao)
            if c2.form_submit_button("🟥 Vermelho", use_container_width=True):
                if nome_cartao and nome_cartao not in st.session_state.sumula_data['red_cards_home']: st.session_state.sumula_data['red_cards_home'].append(nome_cartao)
        
        st.write("**Cartões Registrados (Casa):**")
        for nome in st.session_state.sumula_data['yellow_cards_home']: st.text(f"🟨 {nome}")
        for nome in st.session_state.sumula_data['red_cards_home']: st.text(f"🟥 {nome}")


with col_away:
    with st.container(border=True):
        st.subheader("🟦 Time Visitante")
        away_name = st.text_input("Nome do Time Visitante", value="ADVERSÁRIO", key="away_name")
        away_score = sum(st.session_state.sumula_data['goals_away'].values())
        st.metric("Placar", away_score)
        
        with st.form("away_goal_form", clear_on_submit=True):
            st.markdown("**Adicionar Gol**")
            nome = st.text_input("Nome do Jogador (Gol)", key="a_g_n")
            camisa = st.number_input("Camisa (Gol)", min_value=1, max_value=99, step=1, key="a_g_c")
            qtd = st.number_input("Qtd. Gols", min_value=1, max_value=10, step=1, value=1, key="a_g_q")
            if st.form_submit_button("➕ Adicionar Gol"):
                chave = (nome, int(camisa))
                st.session_state.sumula_data['goals_away'][chave] = st.session_state.sumula_data['goals_away'].get(chave, 0) + qtd

        st.write("**Gols Registrados (Visitante):**")
        for (nome, camisa), qtd in st.session_state.sumula_data['goals_away'].items():
            st.text(f"⚽ {nome} ({camisa}) - {qtd} gol(s)")
            
        st.write("---")
        with st.form("away_card_form", clear_on_submit=True):
            st.markdown("**Adicionar Cartão**")
            nome_cartao = st.text_input("Nome do Jogador (Cartão)", key="a_c_n")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("🟨 Amarelo", use_container_width=True):
                if nome_cartao and nome_cartao not in st.session_state.sumula_data['yellow_cards_away']: st.session_state.sumula_data['yellow_cards_away'].append(nome_cartao)
            if c2.form_submit_button("🟥 Vermelho", use_container_width=True):
                if nome_cartao and nome_cartao not in st.session_state.sumula_data['red_cards_away']: st.session_state.sumula_data['red_cards_away'].append(nome_cartao)

        st.write("**Cartões Registrados (Visitante):**")
        for nome in st.session_state.sumula_data['yellow_cards_away']: st.text(f"🟨 {nome}")
        for nome in st.session_state.sumula_data['red_cards_away']: st.text(f"🟥 {nome}")

# --- Ocorrências Gerais ---
st.write("---")
st.header("📌 Ocorrências Gerais")

# Função auxiliar para criar as seções de ocorrências
def create_occurrence_section(title, key, placeholder):
    with st.container(border=True):
        st.subheader(title)
        
        # Adicionar item
        new_item = st.text_input(f"Adicionar a {title}", key=f"add_{key}", placeholder=placeholder)
        if st.button(f"➕ Adicionar a {title}", key=f"btn_add_{key}"):
            if new_item and new_item not in st.session_state.sumula_data[key]:
                st.session_state.sumula_data[key].append(new_item)
                st.rerun()

        # Remover itens
        if st.session_state.sumula_data[key]:
            items_to_remove = st.multiselect(f"Remover de {title}", options=st.session_state.sumula_data[key], key=f"rem_{key}")
            if st.button(f"🗑️ Remover Selecionados de {title}", key=f"btn_rem_{key}"):
                st.session_state.sumula_data[key] = [item for item in st.session_state.sumula_data[key] if item not in items_to_remove]
                st.rerun()
        
        # Exibir lista atual
        st.write(f"**Lista Atual:** {', '.join(st.session_state.sumula_data[key]) or 'Nenhum'}")


c1, c2, c3 = st.columns(3)
with c1:
    create_occurrence_section("🚫 Suspensos", "suspensos", "Nome do jogador suspenso")
    create_occurrence_section("📌 Faltas não justificadas", "faltas_nao", "Nome de quem faltou")
with c2:
    create_occurrence_section("📆 Cumpriu Suspensão", "cumpriu_suspensao", "Nome de quem voltou")
    create_occurrence_section("✅ Faltas justificadas", "faltas_sim", "Nome (motivo)")
with c3:
    create_occurrence_section("🚑 Departamento Médico", "medico", "Nome (lesão)")
    create_occurrence_section("🟨 Cartões (Mês)", "cartoes_mes", "Nome (2 amarelos)")


# --- Prévia e Geração ---
st.write("---")
st.header("📄 Prévia da Súmula")

dados_jogo_dict = {
    'data': data_jogo.strftime("%d-%m-%Y"), 'dia': dia_semana, 'rodada': rodada,
    'gol_do_jogo': gol_jogo, 'goleiro_do_jogo': goleiro_jogo, 'craque_do_jogo': craque_jogo,
    'home_name': home_name, 'away_name': away_name
}
sumula_final = montar_sumula_texto(dados_jogo_dict)
st.code(sumula_final)

# --- Controles de Salvamento ---
st.write("---")
st.header("💾 Salvar Súmula")
c1, c2 = st.columns(2)
nome_base_arquivo = f"sumula_{data_jogo.strftime('%d-%m-%Y')}"
caminho_sumulas = data_manager.SUMULA_LEGACY_DIR

if c1.button("Salvar Súmula (TXT)", use_container_width=True, type="primary"):
    caminho_completo = os.path.join(caminho_sumulas, f"{nome_base_arquivo}.txt")
    with open(caminho_completo, "w", encoding="utf-8") as f:
        f.write(sumula_final)
    st.success(f"Súmula salva em: {caminho_completo}")

if REPORTLAB_AVAILABLE and c2.button("Exportar PDF", use_container_width=True):
    caminho_completo_pdf = os.path.join(caminho_sumulas, f"{nome_base_arquivo}.pdf")
    doc = SimpleDocTemplate(caminho_completo_pdf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = [Preformatted(sumula_final, getSampleStyleSheet()["Code"])]
    doc.build(story)
    st.success(f"PDF exportado para: {caminho_completo_pdf}")