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
from src.backend.dbconnection import dbconnection
import src.backend.estoque as estoque
from src.backend.produtos import Salgado, Bebida

manager = estoque.EstoqueManager()
fin = finance.Financeiro()


st.set_page_config(
    page_title="Customer Menu",
    page_icon="🛎️"
)

def menucliente():
    tab_compras, tab_perfil = st.tabs(["🛒 Fazer Pedido", "👤 Meus Dados & Descontos"])

    user_id = st.session_state.get("user_id")


    with tab_perfil:
        st.subheader("👤 Meu Perfil")
        db = dbconnection()
        
        # Busca os dados atuais do cliente
        user_data = db.fetch_one(
            'SELECT "user", time_coracao, assiste_one_piece, cidade FROM credentials_customer WHERE id = %s',
            (user_id,)
        )

        if user_data:
            nome_at, time_at, op_at, city_at = user_data
            with st.form("perfil_form"):
                st.write(f"Usuário: **{nome_at}**")
                
               
                novo_time = st.text_input("Alterar Time do Coração", value=time_at if time_at else "")
                
                novo_op = st.selectbox(
                    "Você assiste One Piece?", 
                    options=[True, False], 
                    index=0 if op_at else 1,
                    format_func=lambda x: "Sim" if x else "Não"
                )
                
                nova_city = st.text_input("Sua Cidade", value=city_at if city_at else "")
                
                if st.form_submit_button("Salvar Alterações"):
                    sql_up = 'UPDATE credentials_customer SET time_coracao=%s, assiste_one_piece=%s, cidade=%s WHERE id=%s'
                    if db.execute_command(sql_up, (novo_time, novo_op, nova_city, user_id)):
                        st.success("✅ Perfil atualizado com sucesso!")
                        st.rerun()
        
        st.divider()

        st.subheader("📜 Meu Histórico de Pedidos")
        
        # Busca VIEW filtrando pelo ID do cliente logado
        query_hist = """
            SELECT data_hora, valor_total, detalhe_itens 
            FROM vw_historico_pedidos 
            WHERE cliente_id = %s
            ORDER BY data_hora DESC
        """
        historico = db.fetch_all(query_hist, (user_id,))

        if historico:
            df_hist = pd.DataFrame(historico, columns=["Data/Hora", "Valor Total", "Itens do Pedido"])
            
        
            df_hist["Valor Total"] = df_hist["Valor Total"].map("R$ {:.2f}".format)
            
            st.dataframe(
                df_hist, 
                width='stretch',
                hide_index=True
            )
        else:
            st.info("Você ainda não realizou nenhum pedido. Que tal um salgado agora?")

        st.divider()

        if st.button("Sair da Conta (Logout)", type="secondary"):
            st.session_state.valid1 = False
            st.rerun()
        db.end_connection()

   
    with tab_compras:
        st.title("🛎️ Menu de Compras")

        if "reset_vendas" not in st.session_state:
            st.session_state.reset_vendas = 0

        if st.session_state.get("compra_finalizada", False):
            st.balloons()
            st.success("✅ Compra Concluída! Volte Sempre!")
            st.session_state.compra_finalizada = False
        
        itens_estoque = manager.pesquisar_estoque("", "") 
        
        if not itens_estoque:
            st.warning("O cardápio está vazio.")
            return

        if "pedido_atual" not in st.session_state:
            st.session_state.pedido_atual = {}

        # Busca/Filtros
        st.write("### 🔍 Buscar Produtos ")
        col_f1, col_f2, col_f3 = st.columns([1,1.2,1.3])
        with col_f1:
            cat_filtro = st.pills("Categoria", ["Todos", "Salgado", "Bebida"], default="Todos")
        with col_f2:
            busca_nome = st.text_input("Pesquisar por nome", placeholder="Ex: Coxinha")
        with col_f3:
            busca_sabor = st.text_input("Sabor", placeholder="Ex: Frango")

        if cat_filtro is None: cat_filtro = "Todos"

        itens_exibidos = [
            i for i in itens_estoque 
            if (cat_filtro == "Todos" or i.categoria == cat_filtro) and
               (busca_nome.lower() in i.nome.lower()) and
               (busca_sabor.lower() in i.sabor.lower())
        ]

        st.divider()
        st.write("### 🍕 Escolha seus produtos")
        
        col_nome, col_sabor, col_preco, col_estoque, col_pedir = st.columns([2, 1.5, 1, 1, 1.2])
        col_nome.write("**Produto**")
        col_sabor.write("**Sabor**")
        col_preco.write("**Preço**")
        col_estoque.write("**Estoque**")
        col_pedir.write("**Qtd**")

        for item in itens_exibidos:
            chave = f"item_{item.categoria}_{item.id}_{st.session_state.reset_vendas}"
            valor_anterior = st.session_state.pedido_atual[chave]['qtd'] if chave in st.session_state.pedido_atual else 0
            
            c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 1.2])
            c1.write(item.nome)
            c2.write(f"_{item.sabor}_")
            c3.write(f"R$ {float(item.valor):.2f}")
            c4.write(f"{int(item.quantia)}") 
            
            qtd = c5.number_input("Pedir", 0, int(item.quantia), value=valor_anterior, step=1, key=chave, label_visibility="collapsed")
            
            if qtd > 0:
                st.session_state.pedido_atual[chave] = {
                    "id": item.id, "nome": item.nome, "cat": item.categoria, 
                    "qtd": qtd, "subtotal": qtd * float(item.valor), "sabor": item.sabor
                }
            else:
                st.session_state.pedido_atual.pop(chave, None)

        # RESUMO da cimpra e confirmacao
        if st.session_state.pedido_atual:
            st.divider()
            st.subheader("🛒 Resumo do seu Carrinho")
            
            total_bruto = 0.0
            for info in st.session_state.pedido_atual.values():
                col_res1, col_res2, col_res3 = st.columns([3, 1, 1])
                col_res1.write(f"**{info['nome']}** ({info['sabor']})")
                col_res2.write(f"{info['qtd']} un")
                col_res3.write(f"R$ {info['subtotal']:.2f}")
                total_bruto += info['subtotal']

            # --- DESCONTO ---
            taxa_desc = 0.0
            db = dbconnection()
            perfil = db.fetch_one('SELECT time_coracao, assiste_one_piece, cidade FROM credentials_customer WHERE id = %s', (user_id,))
            db.end_connection()

            if perfil:
                t_cor, op_bool, c_city = perfil
                if t_cor and t_cor.lower().strip() == "flamengo": taxa_desc += 0.05
                if op_bool: taxa_desc += 0.05
                if c_city and c_city.lower().strip() == "sousa": taxa_desc += 0.10

            valor_final = total_bruto * (1 - taxa_desc)

            st.divider()
            st.subheader("💳 Finalizar Pagamento")

            #verifica se há vendedor logado para compra ser efetivada
            vendedor_id = st.session_state.get("salesman_id") 
            if not vendedor_id:
                st.error("❌ Erro: Não há vendedor logado para efetivar a venda.")

            metodo_pag = st.selectbox("Selecione a Forma de Pagamento", ["Cartão", "Boleto", "Pix", "Berries"], index=None)

            st.divider()
            col_met1, col_met2 = st.columns(2)
            col_met1.metric("Subtotal", f"R$ {total_bruto:.2f}")
            col_met2.metric("Total Final", f"R$ {valor_final:.2f}", 
                           delta=f"-{taxa_desc*100:.0f}%" if taxa_desc > 0 else None)
            
            confirmar = st.checkbox("Confirmar Pedido")

            # O botão só habilita se: Checkbox marcado + Vendedor logado + Método selecionado
            pode_finalizar = confirmar and vendedor_id and metodo_pag

            if st.button("Finalizar Compra", type="primary", disabled=not pode_finalizar):
                itens_para_venda = []
                sucesso_estoque = True
                
                for info in list(st.session_state.pedido_atual.values()):
                    if manager.baixar_estoque(info['id'], info['cat'], info['qtd']) > 0:
                        itens_para_venda.append({
                            'nome': info['nome'], 'sabor': info['sabor'], 
                            'qtd': info['qtd'], 'preco_unitario': info['subtotal'] / info['qtd']
                        })
                    else:
                        sucesso_estoque = False
                        st.error(f"Erro de estoque para: {info['nome']}")

                if sucesso_estoque and itens_para_venda:
                    status_pag = "Confirmado" if metodo_pag in ["Pix", "Berries","Cartão","Boleto"] else "Pendente"
                    
                    sucesso_venda = fin.registrar_venda_detalhada(
                        valor_total=valor_final, 
                        itens_do_pedido=itens_para_venda, 
                        cliente_id=user_id,
                        vendedor_id=vendedor_id,
                        metodo_pagamento=metodo_pag,
                        status_pagamento=status_pag
                    )

                    if sucesso_venda:
                        st.session_state.compra_finalizada = True
                        st.session_state.pedido_atual = {}
                        st.session_state.reset_vendas += 1
                        st.rerun()
                    else:
                        st.error("Erro ao registrar os dados financeiros da venda.")
                


if not st.session_state.get("valid1", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login: login(type=1, function=menucliente, table="credentials_customer")
    with tab_register: register(table="credentials_customer")
else:
    menucliente()