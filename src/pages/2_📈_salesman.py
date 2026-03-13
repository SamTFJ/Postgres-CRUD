import streamlit as st
from pathlib import Path
import sys
import pandas as pd

root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
from src.backend.register import register
import src.backend.estoque as estoque

st.set_page_config(
    page_title="Vendedor",
    page_icon="📊"
)

def menu_vendedor():
    st.subheader("📦 Gerenciamento de Estoque")

    #abas principais

    aba_cadastro, aba_atualizar, aba_exibir ,aba_alerta= st.tabs(["📝 Cadastrar", "🚛 Reabastecer", "🔍 Pesquisar/Vizualizar", " ⚠️ Estoque Baixo"])

    with aba_cadastro:
    #pills dentro das abas
        tipo_cadastro = st.pills(
            "O que deseja cadastrar?", ["Salgado", "Bebida"], selection_mode="single"
        )

        st.divider() #linha p/ separar selecao do formulario


        if tipo_cadastro == "Salgado":
            st.markdown ("🥟 Cadastro de Salgados")
            with st.form("form_salgado"):
                nome = st.text_input("Nome do Salgado")
                valor = st.number_input("Valor do Salgado (R$)", min_value = 0.0, step = 0.50)
                quantia = st.number_input("Quantia Inicial para o Estoque", min_value = 0, step = 1)
                sabor = st.text_input("Sabor")

                if st.form_submit_button("Adicionar Salgado"):
                    if nome and valor > 0:
                        if estoque.adicionar_salgado(nome,valor,quantia,sabor):
                            st.success(f"{nome} adicionado com sucesso!")
                        else:
                            st.error("Erro ao adicionar salgado")
                    else:
                        st.error("Preencha os campos corretamente!")

        elif tipo_cadastro == "Bebida":
            st.markdown("🥤 Cadastro de Bebidas")
            with st.form("form bebida"):
                nomeb = st.text_input("Nome da bebida")
                valorb = st.number_input("Preço (R$)", min_value=0.0, step=0.50)
                quantiab = st.number_input("Quantia Inicial para o Estoque", min_value=0, step=1)
                saborb = st.text_input("Sabor")
                volume = st.number_input("Volume (ml)", min_value = 100, step=50)

                if st.form_submit_button("Adicionar Bebida"):
                    if nomeb and valorb > 0:
                        if estoque.adicionar_bebida(nomeb,valorb,quantiab,saborb,volume):
                            st.success(f"{nomeb} foi adicionada com sucesso")
                        else:
                            st.error("Falha ao acidionar bebida")
                    else:
                        st.warning("Preencha os campos corretamente")

    with aba_atualizar:
        st.write("Reabastecer bebidas ou salgados...")

    with aba_exibir:
        st.write("🔍 Consultar Estoque")

        filtro_categoria = st.pills(
            "Listar por Categoria:", ["Todos", "Salgados","Bebidas"], default = "Todos"
        )

        st.divider()

        st.write("Buscar produto Específico")
        col1,col2 = st.columns(2)
        with col1:
            busca_nome = st.text_input("Nome do item", placeholder="Ex: Coxinha")
        with col2:
            busca_sabor = st.text_input("Sabor", placeholder="Ex: Frango")

        # a exibiçãp é baseada na escolha das pills e da busca

        if busca_nome or busca_sabor:
            dados = estoque.pesquisar_estoque(busca_nome,busca_sabor)
        else:
            #se nao ha busca por texto, filtra por categoria
            if filtro_categoria == "Salgados":
                dados = estoque.listar_salgados()
            elif filtro_categoria == "Bebidas":
                dados = estoque.listar_bebidas()
            else:
                #função de UNION para mostrar tudo
                dados = estoque.pesquisar_estoque("", "")
        if dados:
            colunas = ["Nome", "Preço", "Qtd", "Sabor", "Volume", "Categoria"] #dataframe
            df = pd.DataFrame(dados, columns=colunas) #transforma df de lista para tabela
            st.write(f"Exibindo {len(df)} item(ns):")
            st.dataframe(df, width="stretch")
            
        else:
            st.info("Nenhum item encontrado com esses filtros até o momento")


    with aba_alerta:
        st.write("🚨 Itens Precisando de Reposição")
        criticos = estoque.listar_estoque_critico()
        
        if criticos:
            colunas = ["Nome", "Preço", "Qtd", "Sabor", "Volume", "Categoria"]
            df = pd.DataFrame(criticos, columns=colunas) #transforma df de lista para tabela
            st.warning(f"Existem {len(df)} produtos acabando!")
            st.table(df)
        else:
            st.success("Estoque saudável! Nenhum item abaixo de 5 unidades.")



if not st.session_state.get("valid2", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=2, function=menu_vendedor, table="credentials_salesman")

    with tab_register:
        register(table="credentials_salesman")
else:
    login(type=2, function=menu_vendedor, table="credentials_salesman")