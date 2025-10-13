# app_sjfc_streamlit.py
import streamlit as st
import data_manager
import json
from datetime import datetime
import time

# Configuração da página (deve ser o primeiro comando Streamlit)
st.set_page_config(
    page_title="São Jorge FC - Central",
    page_icon="⚽",
    layout="wide"
)

# Carrega e inicializa os dados
data_manager.initialize_session_state()

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.image("logo_sao_jorge.png", width=150)
    st.title("São Jorge FC")
    st.write("---")

    # Botão para salvar alterações
    if st.button("💾 Salvar Todas as Alterações", use_container_width=True, type="primary"):
        data_manager.save_data()

    st.write("---")
    st.header("Opções do Sistema")

    # Funcionalidade de Backup
    dados_json = json.dumps(st.session_state.get('dados', {}), indent=4, ensure_ascii=False)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="📥 Fazer Backup dos Dados",
        data=dados_json,
        file_name=f"backup_sjfc_{timestamp}.json",
        mime="application/json",
        use_container_width=True
    )

    # Funcionalidade de Restauração
    uploaded_file = st.file_uploader("Restaurar de Backup (.json)", type="json")
    if uploaded_file is not None:
        try:
            new_data = json.load(uploaded_file)
            st.session_state['dados'] = new_data
            data_manager.save_data()
            st.success("Dados restaurados com sucesso! A página será recarregada.")
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao restaurar o backup: {e}")


# --- Página Principal ---
st.title("⚽ Central de Dados do São Jorge FC")
st.markdown("##### // Monitoramento de Performance de Atletas //")
st.write("---")
st.header("Bem-vindo!")
st.write("""
Use o menu na barra lateral para navegar entre as seções:

-   **Gerenciar Jogadores:** Cadastre, edite e visualize os atletas do clube.
-   **Mensalidades:** Controle os pagamentos mensais de cada jogador.
-   **Nova Súmula:** Registre todos os detalhes de uma partida.
-   **Sorteio de Times:** Divida os jogadores em duas equipes de forma equilibrada.

**Importante:** Após fazer alterações (cadastrar um jogador, alterar um pagamento, etc.), clique no botão **"Salvar Todas as Alterações"** na barra lateral para garantir que seus dados sejam persistidos.
""")

# Checar mensalidades atrasadas no início
current_year = str(datetime.now().year)
current_month = str(datetime.now().month)
overdue_players = []

payments_this_year = st.session_state.dados.get('monthly_payments', {}).get(current_year, {})
for player_id, payments in payments_this_year.items():
    if payments.get(current_month, "Atrasada") == "Atrasada":
        player_name = data_manager.get_player_name_by_id(player_id)
        if player_name != "Jogador não encontrado":
            overdue_players.append(player_name)

if overdue_players:
    st.warning(f"**Atenção:** Há {len(overdue_players)} jogador(es) com a mensalidade do mês atual atrasada: {', '.join(overdue_players)}")
else:
    st.success("Todas as mensalidades do mês atual estão em dia!")