import streamlit as st

st.set_page_config(
    page_title="Lanchonete",
    page_icon="🥘",
    layout="wide"
)

def menuprincipal():
    st.title("Lanchonete SABOR 🥘 ")
    st.info("Seja bem-vindo! Use o menu lateral para navegar.")

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

