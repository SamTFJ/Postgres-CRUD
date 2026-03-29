from src.backend.dbconnection import dbconnection
import json

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
        comando = """
            SELECT id, data_hora, origem, valor, tipo, status_pagamento, nome_cliente, nome_vendedor FROM vw_financeiro_detalhado 
            ORDER BY data_hora DESC;
        """
        dados = db.fetch_all(comando)
        db.end_connection()
        return dados
    
    
    def registrar_venda_detalhada(self, valor_total, itens_do_pedido, cliente_id=None, vendedor_id=None, metodo_pagamento=None, status_pagamento=None):
        db = dbconnection()
        try:
            # Converte itens para JSONB — a procedure cuida da inserção em vendas, itens_venda e financeiro
            itens_json = json.dumps([
                {
                    "nome": item["nome"],
                    "sabor": item["sabor"],
                    "qtd": item["qtd"],
                    "preco_unitario": float(item["preco_unitario"])
                }
                for item in itens_do_pedido
            ])

            db.cur.execute(
                "CALL sp_registrar_venda(%s, %s, %s, %s, %s, %s::jsonb);",
                (valor_total, cliente_id, vendedor_id, metodo_pagamento, status_pagamento, itens_json)
            )
            db.conn.commit()
            return True
        except Exception as e:
            print(f"Erro na stored procedure sp_registrar_venda: {e}")
            db.conn.rollback()
            return False
        finally:
            db.end_connection()

    def ranking_vendas(self):
        db = dbconnection()
        comando = """
            SELECT produto_nome,  produto_sabor, SUM(quantidade) as qtd_total,SUM(quantidade * preco_unitario) as faturamento_total FROM itens_venda
            GROUP BY produto_nome, produto_sabor
            ORDER BY qtd_total DESC
            LIMIT 5;
        """
        dados = db.fetch_all(comando)
        db.end_connection()
        return dados

    def relatorio_mensal_vendedor(self):
        db = dbconnection()
        comando = """
            SELECT vendedor, mes, total_vendas, faturamento_total, ticket_medio
            FROM vw_relatorio_mensal_vendedor;
        """
        dados = db.fetch_all(comando)
        db.end_connection()
        return dados