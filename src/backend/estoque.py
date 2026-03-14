from .dbconnection import dbconnection
import src.backend.financeiro as fin

##===========CADASTRO DE ALIMENTOS E BEBIDAS============

def adicionar_salgado(nome,sabor,valor,quantia):
    #insere um novo registro na tabela de salgados
    db = dbconnection()

    #usa %s para evitar sql injection
    comando = """
        INSERT INTO salgados (nome,sabor,valor,quantia_estoque)
        VALUES (%s,%s,%s,%s);
    """
    parametros = (nome,sabor,valor,quantia)

    sucesso = db.execute_command(comando,parametros)
    db.end_connection()
    return sucesso

def adicionar_bebida(nome,sabor,valor,quantia):
    #insere um novo registro na tabela de bebidas
    db = dbconnection()
    comando = """
        INSERT INTO bebidas (nome,sabor,valor,quantia_estoque)
        VALUES (%s,%s,%s,%s);
    """
    parametros = (nome,sabor,valor,quantia)

    sucesso = db.execute_command(comando,parametros)
    db.end_connection()
    return sucesso

##================BUSCA DE ALIMENTOS E BEBIDAS========================

def listar_salgados():
    #busca todos registros da tabela de salgados
    db = dbconnection()
    comando = """
    SELECT id_salgado, nome, sabor, valor, quantia_estoque, 'Salgado' as categoria  
    FROM salgados ORDER BY quantia_estoque DESC;
    """
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados

def listar_bebidas():
    #busca todos registros da tabela de bebidas
    db = dbconnection()
    comando = """
    SELECT id_bebida, nome, sabor, valor, quantia_estoque, 'Bebida' as categoria 
    FROM bebidas ORDER BY quantia_estoque DESC
        """
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados

def listar_estoque_critico():
    #busca todos os registros de todas tabelas que possuem menos de 5 unidades
    db = dbconnection()
    # o join ele "junta" as tabelas, ja o union faz uma lista vertical com tudo. FIca melhor para visualização
    comando = """
        SELECT id_salgado, nome, sabor, valor, quantia_estoque, 'Salgado' as categoria 
        FROM salgados
        WHERE quantia_estoque < 5
        
        UNION ALL

        SELECT id_bebida,nome, sabor, valor, quantia_estoque, 'Bebida' as categoria 
        FROM bebidas
        WHERE quantia_estoque < 5

        ORDER BY quantia_estoque DESC;
    """
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados

def pesquisar_estoque(nome_busca, sabor_busca):
    db = dbconnection()
    # o ILIKE busca as partes do texto ignorando letras maiusculas/minusculas
    comando = """
        SELECT id_salgado, nome, sabor, valor, quantia_estoque, 'Salgado' as categoria 
        FROM salgados
        WHERE nome ILIKE %s AND sabor ILIKE %s
        UNION ALL
        SELECT id_bebida, nome, sabor, valor, quantia_estoque, 'Bebida' as categoria 
        FROM bebidas
        WHERE nome ILIKE %s AND sabor ILIKE %s
        ORDER BY quantia_estoque DESC;
    """
    # o primeiro parametro n s é para salgados e o seungo n s é para bebidas
    n = f"%{nome_busca}%"
    s = f"%{sabor_busca}%"
    parametros = (n,s,n,s)

    dados = db.fetch_all(comando,parametros)
    db.end_connection()
    return dados

##====================BAIXA NO ESTOQUE DE ACORDO COM AS COMPRAS DOS CLIENTES==================

def baixar_estoque(id_item, categoria, qtd_desejada):
    db = dbconnection()
    tabela = "salgados" if categoria == "Salgado" else "bebidas"
    coluna_id = "id_salgado" if categoria == "Salgado" else "id_bebida"
    
    # verificar quanto tem no estoque
    check_sql = f"SELECT quantia_estoque FROM {tabela} WHERE {coluna_id} = %s"
    resultado = db.fetch_one(check_sql, (id_item,))
    
    if not resultado or resultado[0] <= 0:
        db.end_connection()
        return 0  # estoque esgotado
    
    estoque_atual = resultado[0]
    
    # limite se pedir 10 e tiver 7, vende 7
    qtd_final = min(qtd_desejada, estoque_atual)
    
    # vende
    update_sql = f"UPDATE {tabela} SET quantia_estoque = quantia_estoque - %s WHERE {coluna_id} = %s"
    db.execute_command(update_sql, (qtd_final, id_item))
    
    db.end_connection()
    return qtd_final  # retorna o q foi vendido



##=====================REABASTECIMENTO DA LANCHONETE======================================

def listar_fabrica():
    db = dbconnection()
    comando = "SELECT nome,sabor,categoria,valor_custo FROM fabrica ORDER BY nome;"
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados

def comprar_da_fabrica(nome, sabor, categoria, quantidade, valor_custo):
    db = dbconnection()
    tabela = "salgados" if categoria == "Salgado" else "bebidas"
    custo_total = quantidade * valor_custo

    #  atualiza o estoque local
    comando_estoque = f"""
        UPDATE {tabela} 
        SET quantia_estoque = quantia_estoque + %s 
        WHERE nome = %s AND sabor = %s;
    """
    
    #  verificar quantas linhas foram alteradas
    db.cur.execute(comando_estoque, (quantidade, nome, sabor))
    db.conn.commit()
    
    # Verifica se o item existia no estoque local
    if db.cur.rowcount > 0:
        # só registra a saída financeira se o estoque foi atualizado com sucesso
        origem = f"Compra Fábrica: {quantidade}x {nome} ({sabor})"
        fin.registrar_movimentacao(origem, custo_total, "SAIDA")
        db.end_connection()
        return True
    else:
        # Se rowcount for 0 o item não existe na tabela de salgados/bebidas
        db.end_connection()
        return False