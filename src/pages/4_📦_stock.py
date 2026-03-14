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
    page_title="Estoque",
    page_icon="📦"
)

def menu_vendedor():
    st.title("📦 Gerenciamento de Estoque")

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
                sabor = st.text_input("Sabor")
                valor = st.number_input("Valor do Salgado (R$)", min_value = 0.0, step = 0.50)
                quantia = st.number_input("Quantia Inicial para o Estoque", min_value = 0, step = 1)
                

                if st.form_submit_button("Adicionar Salgado"):
                    if nome.strip() and sabor.strip() and valor > 0:
                        if estoque.adicionar_salgado(nome,sabor,valor,quantia):
                            st.success(f"{nome} adicionado com sucesso!")
                        else:
                            st.error("❌ Erro ao adicionar salgado!")
                    else:
                        st.error("⚠️ Preencha os campos corretamente!")

        elif tipo_cadastro == "Bebida":
            st.markdown("🥤 Cadastro de Bebidas")
            with st.form("form bebida"):
                nomeb = st.text_input("Nome da bebida")
                saborb = st.text_input("Sabor")
                valorb = st.number_input("Preço (R$)", min_value=0.0, step=0.50)
                quantiab = st.number_input("Quantia Inicial para o Estoque", min_value=0, step=1)

                if st.form_submit_button("Adicionar Bebida"):
                    if nomeb.strip() and saborb.strip() and valorb > 0:
                        if estoque.adicionar_bebida(nomeb,saborb,valorb,quantiab):
                            st.success(f"{nomeb} foi adicionada com sucesso")
                        else:
                            st.error("❌ Falha ao acidionar bebida!")
                    else:
                        st.warning("⚠️ Preencha os campos corretamente!")

    with aba_atualizar:
        st.subheader("🏭 Pedido à Fábrica")
        
        itens_fabrica = estoque.listar_fabrica()
        
        if itens_fabrica:
            opcoes = [f"{item[0]} ({item[1]})" for item in itens_fabrica]
            escolha = st.selectbox("Selecione o produto da Fábrica", opcoes)
            
            idx = opcoes.index(escolha)
            item_sel = itens_fabrica[idx] # (nome, sabor, categoria, valor_custo)
            
            col1, col2 = st.columns(2)
            with col1:
                qtd_compra = st.number_input("Quantidade", min_value=1, step=1, key="qtd_f")
            with col2:
                preco_custo = float(item_sel[3])
                st.text_input("Preço de Custo Unitário", value=f"R$ {preco_custo:.2f}", disabled=True)
            
            # calculo do total q
            total_financeiro = qtd_compra * preco_custo
            st.info(f"💰 **Total a ser descontado do caixa: R$ {total_financeiro:.2f}**")

            # botão de confirmação com um checkbox de segurança 
            confirmar = st.checkbox("Confirmo os valores acima")
            
            if st.button("Finalizar Compra", disabled=not confirmar):
                sucesso = estoque.comprar_da_fabrica(
                    item_sel[0], item_sel[1], item_sel[2], qtd_compra, preco_custo
                )
                
                if sucesso:
                    st.toast(f"✅ Compra de {item_sel[0]} realizada!", icon = '💰')
                    st.success(f"✅ Sucesso! R$ {total_financeiro:.2f} descontados do caixa.")
                else:
                    st.error("❌ Erro: Este item precisa ser cadastrado antes.")
        else:
            st.warning("O catálogo da fábrica está vazio.")


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
            colunas = ["ID", "Nome", "Sabor","Preço (R$)", "Quantia", "Categoria"] #dataframe
            df = pd.DataFrame(dados, columns=colunas) #transforma df de lista para tabela
            st.write(f"Exibindo {len(df)} item(ns):")
            st.dataframe(df, width="stretch")
            
        else:
            st.info("Nenhum item encontrado com esses filtros até o momento")


    with aba_alerta:
        st.write("🚨 Itens Precisando de Reposição")
        criticos = estoque.listar_estoque_critico()
        
        if criticos:
            colunas = ["ID","Nome","Sabor", "Preço (R$)", "Quantia", "Categoria"]
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