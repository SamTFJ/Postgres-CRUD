from src.backend.dbconnection import dbconnection

class Financeiro:

    def __init__(self):
         pass

    def saldo_atual(self):
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


    def registrar_movimentacao(self,origem, valor, tipo, cliente_id=None, vendedor_id=None):
        db = dbconnection()
        comando = """
            INSERT INTO financeiro (origem, valor, tipo, cliente_id, vendedor_id) 
            VALUES (%s, %s, %s, %s, %s);
        """
        parametros = (origem, valor, tipo, cliente_id, vendedor_id)
        db.execute_command(comando, parametros)
        db.end_connection()


    def relatorio_financeiro_detalhado(self):
        db = dbconnection()
        #view mais detalhado para ver relatorio
        comando = "SELECT data_hora, origem, valor, tipo, nome_vendedor, nome_cliente FROM vw_financeiro_detalhado ORDER BY data_hora DESC;"
        dados = db.fetch_all(comando)
        db.end_connection()
        return dados
    
    
    def registrar_venda_detalhada(self, valor_total, itens_do_pedido, cliente_id=None, vendedor_id=None):
        db = dbconnection()
        try:
            
            query_venda = "INSERT INTO vendas (valor_total, cliente_id, vendedor_id) VALUES (%s, %s, %s) RETURNING id_venda;"
            db.cur.execute(query_venda, (valor_total, cliente_id, vendedor_id))
            id_venda = db.cur.fetchone()[0]

            query_item = """
                INSERT INTO itens_venda (venda_id, produto_nome,produto_sabor, quantidade, preco_unitario)
                VALUES (%s, %s,%s, %s, %s);
            """
            for item in itens_do_pedido:
                db.cur.execute(query_item, (id_venda, item['nome'],item['sabor'],item['qtd'], item['preco_unitario']))
            
            self.registrar_movimentacao(f"Venda #{id_venda}", valor_total, "ENTRADA", cliente_id, vendedor_id)

            db.conn.commit()
            return True
        except Exception as e:
            print(f"Erro na transação: {e}")
            db.conn.rollback()
            return False
        finally:
            db.end_connection()

    def ranking_vendas(self):
            db = dbconnection()
            comando = "SELECT * FROM vw_ranking_vendas LIMIT 5;"
            dados = db.fetch_all(comando)
            db.end_connection()
            return dados