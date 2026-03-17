import streamlit as st
from pathlib import Path
import sys
import pandas as pd


root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
import src.backend.financeiro as finance
fin = finance.Financeiro()

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

    historico = fin.relatorio_financeiro_detalhado()
    
    if historico:
        df_financeiro = pd.DataFrame(
            historico,
            columns=["Data", "Descrição", "Valor (R$)", "Operação"]
        )
        
        def colorir_tipo(val):
            color = '#155724' if val == 'ENTRADA' else '#721c24'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_financeiro.style.map(colorir_tipo, subset=['Operação']),
            width="stretch",
            hide_index=True
        )
    else:
        st.info("Nenhuma movimentação registrada até o momento.")

if not st.session_state.get("valid2", False):
    tab_login, = st.tabs(["Login"])
    with tab_login:
        login(type=2, function=menu_economia, table="credentials_salesman")
else:
    
    login(type=2, function=menu_economia, table="credentials_salesman")