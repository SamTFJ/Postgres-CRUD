from .dbconnection import dbconnection

def adicionar_salgado(nome,valor,quantia,sabor):
    #insere um novo registro na tabela de salgados
    db = dbconnection()

    #usa %s para evitar sql injection
    comando = """
        INSERT INTO salgados (nome,valor,quantia_estoque, sabor)
        VALUES (%s,%s,%s,%s);
    """
    parametros = (nome,valor,quantia,sabor)

    sucesso = db.execute_command(comando,parametros)
    db.end_connection()
    return sucesso

def adicionar_bebida(nome,valor,quantia,sabor,volume):
    #insere um novo registro na tabela de bebidas
    db = dbconnection()
    comando = """
        INSERT INTO bebidas (nome,valor,quantia_estoque,sabor,volume_ml)
        VALUES (%s,%s,%s,%s,%s);
    """
    parametros = (nome,valor,quantia,sabor,volume)

    sucesso = db.execute_command(comando,parametros)
    db.end_connection()
    return sucesso

def listar_salgados():
    #busca todos registros da tabela de salgados
    db = dbconnection()
    comando = """
    SELECT nome, valor, quantia_estoque, sabor, NULL as volume_ml, 'Salgado' as categoria  
    FROM salgados ORDER BY quantia_estoque DESC;
    """
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados

def listar_bebidas():
    #busca todos registros da tabela de bebidas
    db = dbconnection()
    comando = """
    SELECT nome, valor, quantia_estoque, sabor, volume_ml, 'Bebida' as categoria 
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
        SELECT nome, valor, quantia_estoque, sabor, NULL as volume_ml, 'Salgado' as categoria 
        FROM salgados
        WHERE quantia_estoque < 5
        
        UNION ALL

        SELECT nome, valor, quantia_estoque, sabor, volume_ml, 'Bebida' as categoria 
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
        SELECT nome, valor, quantia_estoque, sabor, NULL as volume_ml, 'Salgado' as categoria 
        FROM salgados
        WHERE nome ILIKE %s AND sabor ILIKE %s
        UNION ALL
        SELECT nome, valor, quantia_estoque, sabor, volume_ml, 'Bebida' as categoria 
        FROM bebidas
        WHERE nome ILIKE %s AND sabor ILIKE %s
        ORDER BY nome ASC;
    """
    # o primeiro parametro n s é para salgados e o seungo n s é para bebidas
    n = f"%{nome_busca}%"
    s = f"%{sabor_busca}%"
    parametros = (n,s,n,s)

    dados = db.fetch_all(comando,parametros)
    db.end_connection()
    return dados