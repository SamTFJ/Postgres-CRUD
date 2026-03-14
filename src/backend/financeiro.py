from src.backend.dbconnection import dbconnection


def saldo_atual():
    db =dbconnection()

    comando = """
    SELECT
        COALESCE(SUM(CASE WHEN tipo = 'ENTRADA' THEN valor ELSE -valor END), 0) 
        FROM financeiro;
    """
    # o case compara se é entrada (t/f), para definir se o valor é positivo ou negativo, em seguida o sum soma, e o ccoalesce faz com q se a soma seja null, ele retorna 0

    resultado = db.fetch_all(comando)
    db.end_connection()
    return float(resultado[0][0]) if resultado else 0.0


def registrar_movimentacao(origem, valor, tipo, cliente_id=None, vendedor_id=None):
    db = dbconnection()
    comando = """
        INSERT INTO financeiro (origem, valor, tipo, cliente_id, vendedor_id) 
        VALUES (%s, %s, %s, %s, %s);
    """
    parametros = (origem, valor, tipo, cliente_id, vendedor_id)
    db.execute_command(comando, parametros)
    db.end_connection()


def relatorio_financeiro_detalhado():
    db = dbconnection()
    #junta 4 tabelas em um select, o Coalesce faz com que se ocorra uma venda sem o cliente registrdo, vai retornar consumidor final ao inves de null, o mesmo pra vendedor
    comando = """
        SELECT 
            f.data_hora,
            COALESCE(c.user, 'Consumidor Final') as cliente,
            COALESCE(s.user, 'Vendedor') as vendedor,
            f.origem,
            f.valor,
            f.tipo
        FROM financeiro f
        LEFT JOIN credentials_customer c ON f.cliente_id = c.id
        LEFT JOIN credentials_salesman s ON f.vendedor_id = s.id
        ORDER BY f.data_hora DESC;
    """
    dados = db.fetch_all(comando)
    db.end_connection()
    return dados