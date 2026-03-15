import streamlit as st
import pandas as pd
from pathlib import Path
import sys

root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

import src.backend.estoque as estoque
manager = estoque.EstoqueManager()


st.set_page_config(
    page_title="Lanchonete",
    page_icon="🥘",
    layout="wide"
)

def menuprincipal():
    st.title("Lanchonete SABOR 🥘 ")
    st.info("Seja bem-vindo! Use o menu lateral para navegar.")

    st.divider()
    st.subheader("🍕 Nosso Cardápio")
    filtro = st.pills(
        "Filtrar por categoria:",
        options=["Todos", "Salgado", "Bebida"],
        default="Todos"
    )

    if filtro is None:
        filtro = "Todos"

        
    itens = manager.pesquisar_estoque("", "") 
    
    if itens:
        dados_cardapio = []
        for item in itens:
            if filtro == "Todos" or item.categoria == filtro:
                dados_cardapio.append({
                    "Produto": item.nome,
                    "Sabor": item.sabor,
                    "Preço": f"R$ {item.valor:.2f}",
                    "Categoria": item.categoria
                })
        
        if dados_cardapio:
            df_cardapio = pd.DataFrame(dados_cardapio)
            st.dataframe(df_cardapio, width="stretch", hide_index=True)
        else:
            st.info(f"Não há {filtro.lower()}s disponíveis no momento.")
            
    else:
        st.warning("O cardápio está sendo preparado. Volte logo!")


#obj de pagina q aponta para os arquivos existentes
home_page = st.Page(menuprincipal, title="Menu Lanchonete", icon ="🥘", default = True)
customer = st.Page("pages/1_🛎️_customer.py", title="Cliente", icon="🛎️")
salesman = st.Page("pages/2_📈_salesman.py", title="Vendedor", icon="📈")

#paginas escondidas
savings = st.Page("pages/3_💰_savings.py", title="Economias", icon="💰")
stock = st.Page("pages/4_📦_stock.py", title="Estoque", icon="📦")

if st.session_state.get("valid2", False):
    #se for o vendedor q ta logado, vai conseguir ver as aba de gerenciamento
    pg = st.navigation({
        "Principal" : [home_page, customer],
        "Gerenciamento" : [salesman, savings, stock]
    })
else:
    #se nao tiver logado como vendedor, aparece para logar, ou fica como menu para cliente
    pg = st.navigation({
        "Principal" : [home_page, customer],
        "Acesso Funcionário" : [salesman]
    })

#executa
pg.run()

