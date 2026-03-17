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
import src.backend.financeiro as finance
from src.backend.produtos import Salgado, Bebida
manager = estoque.EstoqueManager()
fin = finance.Financeiro()

st.set_page_config(
    page_title="Estoque",
    page_icon="📦"
)

def menu_vendedor():
    st.title("📦 Gerenciamento de Estoque")

    #abas principais

    aba_relatorio,aba_cadastro,aba_remover,aba_atualizar, aba_exibir ,aba_editar, aba_alerta= st.tabs(["📊 Relatório","📝 Cadastrar Produto"," ❌ Remover Produto" ,"🚛 Reabastecer", "🔍 Pesquisar/Vizualizar","✏️ Editar Produto", " ⚠️ Estoque Baixo"])

    with aba_relatorio:
        st.subheader("📊 Resumo do Estoque")
        
        resumo = manager.quantia_total()
        
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.metric("Total de Salgados", f"{resumo['total_salgado']} un")
        with c2:
            st.metric("Total de Bebidas", f"{resumo['total_bebida']} un")
        with c3:
            st.metric("Variedade de Produtos", f"{resumo['tipos_total_produtos']} tipos")
            
        st.divider()
        
        st.write("### Análise de Composição")
        dados_grafico = pd.DataFrame({
            "Categoria": ["Salgados", "Bebidas"],
            "Qtd Variedade": [resumo['tipos_salgado'], resumo['tipos_bebida']]
        })
        st.bar_chart(dados_grafico, x="Categoria", y="Qtd Variedade", color="#131966")
        


    with aba_cadastro:
    #pills dentro das abas
        tipo_cadastro = st.pills(
            "O que deseja cadastrar?", ["Salgado", "Bebida"], selection_mode="single"
        )

        st.divider() 


        if tipo_cadastro == "Salgado":
            st.markdown ("🥟 Cadastro de Salgados")
            with st.form("form_salgado"):
                nome = st.text_input("Nome do Salgado")
                sabor = st.text_input("Sabor")
                valor = st.number_input("Valor do Salgado (R$)", min_value = 0.0, step = 0.50)
                quantia = st.number_input("Quantia Inicial para o Estoque", min_value = 0, step = 1)
                

                if st.form_submit_button("Adicionar Salgado"):
                    if nome.strip() and sabor.strip() and valor > 0:
                        if manager.adicionar_salgado(nome,sabor,valor,quantia):
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
                        if manager.adicionar_bebida(nomeb,saborb,valorb,quantiab):
                            st.success(f"{nomeb} foi adicionada com sucesso")
                        else:
                            st.error("❌ Falha ao acidionar bebida!")
                    else:
                        st.warning("⚠️ Preencha os campos corretamente!")

    with aba_atualizar:
        st.subheader("🏭 Pedido à Fábrica")
        
        itens_fabrica = manager.listar_fabrica()
        saldo_em_caixa = fin.saldo_atual()
        
        if itens_fabrica:
            opcoes = [f"{item.categoria} ({item.nome} {item.sabor})" for item in itens_fabrica]
            escolha = st.selectbox("Selecione o produto da Fábrica", opcoes)
            
            idx = opcoes.index(escolha)
            item_sel = itens_fabrica[idx] # (nome, sabor, categoria, valor_custo)
            
            col1, col2 = st.columns(2)
            with col1:
                qtd_compra = st.number_input("Quantidade", min_value=1, step=1, key="qtd_f")
            with col2:
                preco_custo = float(item_sel.valor)
                st.text_input("Preço de Custo Unitário", value=f"R$ {preco_custo:.2f}", disabled=True)
            
            total_financeiro = qtd_compra * preco_custo

            col_s1, col_s2 = st.columns(2)
            col_s1.metric("Saldo em Caixa", f"R$ {saldo_em_caixa:.2f}")
            col_s2.metric("Custo do Pedido", f"R$ {total_financeiro:.2f}", delta=-total_financeiro, delta_color="inverse")

            if total_financeiro > saldo_em_caixa:
                st.error(f"❌ Saldo insuficiente! Faltam R$ {(total_financeiro - saldo_em_caixa):.2f}")
                bloquear_botao = True
            else:
                st.info(f"💰 **Total a ser descontado do caixa: R$ {total_financeiro:.2f}**")
                bloquear_botao = False


            # botão de confirmação com um checkbox de segurança 
            confirmar = st.checkbox("Confirmar os valores acima", disabled=bloquear_botao)
            
            if st.button("Finalizar Compra", disabled=not confirmar or bloquear_botao):
                resultado = manager.comprar_da_fabrica(
                    item_sel.nome, item_sel.sabor,item_sel.categoria ,qtd_compra, preco_custo
                )
            
                if resultado == True:
                    st.toast(f"✅ Compra realizada!", icon='💰')
                    st.success(f"✅ Sucesso! R$ {total_financeiro:.2f} descontados.")
                    st.rerun()
                elif resultado == "saldo_insuficiente":
                    st.error("❌ A operação foi cancelada: O saldo acabou durante o processamento.")
                else:
                    st.error("❌ Este item precisa ter em seu cadastrado antes.")


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
            dados = manager.pesquisar_estoque(busca_nome,busca_sabor)
        else:
            #se nao ha busca por texto, filtra por categoria
            if filtro_categoria == "Salgados":
                dados = manager.listar_salgados()
            elif filtro_categoria == "Bebidas":
                dados = manager.listar_bebidas()
            else:
                dados = manager.pesquisar_estoque("", "")
        if dados:
            colunas = ["ID", "Nome", "Sabor","Preço (R$)", "Quantia", "Categoria"] #dataframe

            # lista de listas c/ atribusos de cada objeto
            dados_formatados = [
                [obj.id, obj.nome, obj.sabor, obj.valor, obj.quantia, obj.categoria] 
                for obj in dados
            ]

            df = pd.DataFrame(dados_formatados, columns=colunas) #transforma df de lista para tabela
            st.write(f"Exibindo {len(df)} item(ns):")
            st.dataframe(df, width="stretch")
            
        else:
            st.info("Nenhum item encontrado com esses filtros até o momento")


    with aba_alerta:
        st.write("🚨 Itens Precisando de Reposição")
        criticos = manager.listar_estoque_critico()
        
        if criticos:
            colunas = ["ID","Nome","Sabor", "Preço (R$)", "Quantia", "Categoria"]
            df = pd.DataFrame(criticos, columns=colunas) #transforma df de lista para tabela
            st.warning(f"Existem {len(df)} produtos acabando!")
            st.table(df)
        else:
            st.success("Estoque saudável! Nenhum item abaixo de 5 unidades.")

    with aba_remover:
        st.subheader("🗑️ Remover Item")
    
        todos_os_itens = manager.pesquisar_estoque("", "") 
        
        if todos_os_itens:
            opcoes = [f"{item.categoria} | ID: {item.id} - {item.nome} ({item.sabor})" for item in todos_os_itens]
            escolha = st.selectbox("Selecione o item que deseja apagar:", opcoes)
            
            idx = opcoes.index(escolha)
            item_sel = todos_os_itens[idx]
            id_item = item_sel.id
            categoria = item_sel.categoria

            st.divider()
            st.write(f"**Item Selecionado:** {item_sel.nome} - {item_sel.sabor}")
            st.write(f"**Categoria:** {categoria}")
            
            
            confirmar = st.checkbox(f"Confirmo que desejo apagar permanentemente o item {item_sel.nome}")

            if st.button("Remover do Sistema", type="primary", disabled=not confirmar):
                sucesso = manager.remover_item(id_item, categoria)
                
                if sucesso:
                    st.success(f"✅ O item '{item_sel.nome}' foi removido com sucesso!")
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(" ❌ Não foi possível remover o item.")
        else:
            st.info("Não existem itens no estoque para remover.")


    with aba_editar:
        st.subheader("✏️ Editar Informações do Produto")
        
        todos_itens = manager.pesquisar_estoque("", "") 

        if todos_itens:
            opcoes = [f"{item.categoria} | {item.nome} ({item.sabor})" for item in todos_itens]
            escolha = st.selectbox("Selecione o produto para modificar:", opcoes, key="sel_edit")
            
            
            idx = opcoes.index(escolha)
            item_atual = todos_itens[idx]
            
            id_item = item_atual.id
            nome_atual = item_atual.nome
            sabor_atual = item_atual.sabor
            valor_atual = float(item_atual.valor)
            quantia_atual = int(item_atual.quantia)
            categoria_atual = item_atual.categoria

            st.divider()
            
            with st.form("form_edicao"):
                st.info(f"Editando: {nome_atual} (ID: {id_item})")
                
                col1, col2 = st.columns(2)
                with col1:
                    novo_nome = st.text_input("Nome", value=nome_atual)
                    novo_valor = st.number_input("Preço (R$)", min_value=0.0, value=valor_atual, step=0.50)
                with col2:
                    novo_sabor = st.text_input("Sabor", value=sabor_atual)
                    nova_quantia = st.number_input("Estoque Atual", min_value=0, value=quantia_atual, step=1)
                
               
                if st.form_submit_button("Salvar Alterações"):
                    if novo_nome.strip() and novo_sabor.strip():
                        sucesso = manager.editar_item(
                            id_item, categoria_atual, novo_nome, novo_sabor, novo_valor, nova_quantia
                        )
                        if sucesso:
                            st.success("✅ Produto atualizado com sucesso!")
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar banco de dados.")
                    else:
                        st.warning("⚠️ Os campos Nome e Sabor não podem ficar vazios.")
        else:
            st.info("Nenhum item cadastrado para editar.")



if not st.session_state.get("valid2", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=2, function=menu_vendedor, table="credentials_salesman")

    with tab_register:
        register(table="credentials_salesman")
else:
    login(type=2, function=menu_vendedor, table="credentials_salesman")