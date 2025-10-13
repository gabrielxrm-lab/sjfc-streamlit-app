#!/bin/bash

# Cria o arquivo de configuração do Streamlit
mkdir -p ~/.streamlit
echo "[server]\nport = $PORT\nheadless = true\nenableCORS=false\n" > ~/.streamlit/config.toml

# Inicia o aplicativo Streamlit
streamlit run Home.py
