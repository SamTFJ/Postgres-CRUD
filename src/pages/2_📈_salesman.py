import streamlit as st
from pathlib import Path
import sys
import pandas as pd

root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
from src.backend.register import register
import src.backend.financeiro as finance
fin = finance.Financeiro()


st.set_page_config(
    page_title="Vendedor",
    page_icon="📊"
)

def menu_vendedor():
    st.title("🧑‍💼 Menu Vendedor")
    st.subheader("🏆 Top 5 Itens Mais Vendidos")
    
    dados_ranking = fin.ranking_vendas()
    
    if dados_ranking:
        df_ranking = pd.DataFrame(
            dados_ranking, 
            columns=["Produto", "Sabor", "Qtd Vendida", "Faturamento (R$)"]
        )
        
       
        st.write("#### Detalhes")
        st.dataframe(df_ranking, width="stretch", hide_index=True)
            
        st.divider()

        df_ranking["Produto Completo"] = df_ranking["Produto"] + " (" + df_ranking["Sabor"] + ")"

        st.write("#### Volume de Vendas")
        st.bar_chart(data=df_ranking, x="Produto Completo", y="Qtd Vendida", color="#054c7c")

    else:
        st.info("Ainda não há dados de vendas suficientes para gerar o ranking.")


if not st.session_state.get("valid2", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=2, function=menu_vendedor, table="credentials_salesman")

    with tab_register:
        register(table="credentials_salesman")
else:
    login(type=2, function=menu_vendedor, table="credentials_salesman")