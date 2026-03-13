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


def registrar_movimentacao(origem,valor,tipo):
    db = dbconnection()
    comando = "INSERT INTO financeiro (origem,valor,tipo) VALUES (%s,%s,%s)"
    db.end_connection(comando,(origem,valor,tipo))
    db.end_connection()