import streamlit as st
from pathlib import Path
import sys


root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
import src.backend.financeiro as fin

st.set_page_config(
    page_title="Economias",
    page_icon="💰"
)

def menu_economia():
    st.title("💰 Gerenciamento Econômico")

    saldo_atual = fin.saldo_atual()
    valor_format = f"{saldo_atual:,.2f}"
    valor_br = valor_format.replace(",", "X").replace(".", ",").replace("X", ".")

    st.metric(
    label="Dinheiro Total em Caixa", 
    value=f"R$ {valor_br}",
    delta=f"{(saldo_atual - 10000):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )

    st.divider()

    st.subheader("📋 Últimas Movimentações")


if not st.session_state.get("valid2", False):
    tab_login, = st.tabs(["Login"])
    with tab_login:
        login(type=2, function=menu_economia, table="credentials_salesman")
else:
    
    login(type=2, function=menu_economia, table="credentials_salesman")