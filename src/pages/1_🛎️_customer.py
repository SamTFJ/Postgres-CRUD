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
import src.backend.estoque as estoque
from src.backend.produtos import Salgado, Bebida
manager = estoque.EstoqueManager()
fin = finance.Financeiro()


st.set_page_config(
    page_title="Customer Menu",
    page_icon="🛎️"
)

def menucliente():
    st.title("🛎️ Totem de Pedidos")

    if "reset_vendas" not in st.session_state:
        st.session_state.reset_vendas = 0

    # verifica mensagem de compra concluida apos o rerun
    if st.session_state.get("compra_finalizada", False):
        st.balloons()
        st.success("✅ Compra Concluida! Volte Sempre!")
        st.session_state.compra_finalizada = False
    
    #Busca todos os produtos do banco
    itens_estoque = manager.pesquisar_estoque("", "") # Pega tudo
    
    if not itens_estoque:
        st.warning("O cardápio está vazio.")
        return

    #guardar o que o cliente está selecionando
    #session_state para não perder os dados ao interagir
    if "pedido_atual" not in st.session_state:
        st.session_state.pedido_atual = {}

    st.write("### 🍕 Escolha seus produtos")
    
    #cabeçalho da lista
    col_nome, col_sabor, col_preco, col_estoque, col_pedir = st.columns([2, 1.5, 1, 1, 1.2])
    col_nome.write("**Produto**")
    col_sabor.write("**Sabor**")
    col_preco.write("**Preço**")
    col_estoque.write("**Estoque**")
    col_pedir.write("**Qtd**")

    total_geral = 0.0

    #Cria um input para cada item com seu próprio MAX_VALUE
    for item in itens_estoque:
        id_db = item.id
        nome = item.nome
        sabor = item.sabor
        valor = float(item.valor)
        estoque_atual = int(item.quantia) 
        categoria = item.categoria
        
        # id do produto no session_state + contador do reset
        chave = f"item_{categoria}_{id_db}_{st.session_state.reset_vendas}"
        
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1, 1.2])
        
        c1.write(nome)
        c2.write(f"_{sabor}_")
        c3.write(f"R$ {valor:.2f}")
        c4.write(f"{estoque_atual}") 
        
        
        qtd = c5.number_input(
            "Pedir", 
            min_value=0, 
            max_value=estoque_atual, # Bloqueia se exceder o estoque
            step=1, 
            key=chave,
            label_visibility="collapsed"
        )
        
        if qtd > 0:
            total_geral += (qtd * valor)
            st.session_state.pedido_atual[chave] = {
                "id": id_db, "nome": nome, "cat": categoria, 
                "qtd": qtd, "subtotal": qtd * valor, "sabor": sabor
            }
        else:
            # Remove do pedido se a quantidade voltar a zero
            st.session_state.pedido_atual.pop(chave, None)

    # finalização do Pedido
    if total_geral > 0:
        st.divider()
        st.subheader(f"Total do Pedido: :green[R$ {total_geral:.2f}]")
        
        confirmar = st.checkbox("Confirmar Pedido")
        
        if st.button("🛒 Finalizar Compra", type="primary", disabled=not confirmar):
            itens_para_venda = []
            sucesso_estoque = True
            
            
            for info in list(st.session_state.pedido_atual.values()):
                qtd_baixada = manager.baixar_estoque(info['id'], info['cat'], info['qtd'])
                
                if qtd_baixada > 0:
                    itens_para_venda.append({
                        'nome': info['nome'],
                        'sabor': info['sabor'],
                        'qtd': info['qtd'],
                        'preco_unitario': info['subtotal'] / info['qtd']
                    })
                else:
                    sucesso_estoque = False
                    st.error(f"Erro de estoque para: {info['nome']}")

            
            if itens_para_venda:
                
                total_pedido = sum(item['qtd'] * item['preco_unitario'] for item in itens_para_venda)
                
                sucesso_venda = fin.registrar_venda_detalhada(
                    valor_total=total_pedido,
                    itens_do_pedido=itens_para_venda,
                    cliente_id=st.session_state.get("user_id")
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

    with tab_login:
        login(type=1, function=menucliente, table="credentials_customer")

    with tab_register:
        register(table="credentials_customer")
else:
    login(type=1, function=menucliente, table="credentials_customer")