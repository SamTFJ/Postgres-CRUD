from .dbconnection import dbconnection
import src.backend.financeiro as finance
from src.backend.produtos import Salgado, Bebida
fin = finance.Financeiro()

class EstoqueManager:
    def __init__(self):
        
        pass

    ##=========== MÉTODOS ============
    
    def _adicionar_item(self, tabela, nome, sabor, valor, quantia, local_fabricacao="Mari"):
        """Evitar repetição entre salgados e bebidas"""
        db = dbconnection()
        comando = f"INSERT INTO {tabela} (nome, sabor, valor, quantia_estoque, local_fabricacao) VALUES (%s, %s, %s, %s, %s);"
        parametros = (nome, sabor, valor, quantia, local_fabricacao)
        sucesso = db.execute_command(comando, parametros)
        db.end_connection()
        return sucesso

    ##=========== CADASTRO DE ALIMENTOS E BEBIDAS ============

    def adicionar_salgado(self, nome, sabor, valor, quantia, local_fabricacao="Mari"):
        return self._adicionar_item("salgados", nome, sabor, valor, quantia, local_fabricacao)

    def adicionar_bebida(self, nome, sabor, valor, quantia, local_fabricacao="Mari"):
        return self._adicionar_item("bebidas", nome, sabor, valor, quantia, local_fabricacao)

    ##================ BUSCA DE ITENS / RELATORIOS ========================

    def listar_salgados(self):
        db = dbconnection()
        comando = "SELECT id_salgado, nome, sabor, valor, quantia_estoque, 'Salgado' as categoria, local_fabricacao FROM salgados"
        dados = db.fetch_all(comando)
        db.end_connection()
        return [Salgado(d[0], d[1], d[2], float(d[3]), d[4], d[6]) for d in dados]

    def listar_bebidas(self):
        db = dbconnection()
        comando = "SELECT id_bebida, nome, sabor, valor, quantia_estoque, 'Bebida' as categoria, local_fabricacao FROM bebidas"
        dados = db.fetch_all(comando)
        db.end_connection()
        return [Bebida(d[0], d[1], d[2], float(d[3]), d[4], d[6]) for d in dados]
    
    def listar_estoque_critico(self):
        db = dbconnection()
        dados = db.fetch_all("SELECT * FROM vw_estoque_critico;")
        db.end_connection()
        return dados

    def pesquisar_estoque(self, nome_busca, sabor_busca, preco_min=None, preco_max=None, apenas_mari=False):
        db = dbconnection()
        # vw_estoque_geral agora expõe: id, nome, sabor, valor, quantia_estoque, categoria, local_fabricacao
        filtros = ["nome ILIKE %s", "sabor ILIKE %s"]
        parametros = [f"%{nome_busca}%", f"%{sabor_busca}%"]

        if preco_min is not None:
            filtros.append("valor >= %s")
            parametros.append(preco_min)
        if preco_max is not None:
            filtros.append("valor <= %s")
            parametros.append(preco_max)
        if apenas_mari:
            filtros.append("local_fabricacao ILIKE %s")
            parametros.append("Mari")

        where_clause = " AND ".join(filtros)
        comando = f"""
            SELECT id, nome, sabor, valor, quantia_estoque, categoria, local_fabricacao
            FROM vw_estoque_geral
            WHERE {where_clause}
            ORDER BY quantia_estoque DESC;
        """
        dados = db.fetch_all(comando, tuple(parametros))
        db.end_connection()

        lista_objetos = []
        for d in dados:
            if d[5] == "Salgado":
                lista_objetos.append(Salgado(d[0], d[1], d[2], float(d[3]), d[4], d[6]))
            else:
                lista_objetos.append(Bebida(d[0], d[1], d[2], float(d[3]), d[4], d[6]))

        return lista_objetos
    
    def quantia_total(self):
        db = dbconnection()

        comando_salgado = "SELECT SUM(quantia_estoque) FROM salgados"
        dado_S = db.fetch_one(comando_salgado)
        total_salgado = dado_S[0] if dado_S and dado_S[0] else 0
        
        comando_bebida = "SELECT SUM(quantia_estoque) FROM bebidas"
        dado_B = db.fetch_one(comando_bebida)
        total_bebida = dado_B[0] if dado_B and dado_B[0] else 0

        tipos_salgado = db.fetch_one("SELECT COUNT(*) FROM salgados")[0] or 0
        tipos_bebida = db.fetch_one("SELECT COUNT(*) FROM bebidas")[0] or 0

        db.end_connection()

        return{
            "total_salgado": total_salgado,
            "total_bebida": total_bebida,
            "tipos_salgado" : tipos_salgado,
            "tipos_bebida": tipos_bebida,
            "tipos_total_produtos" : tipos_bebida + tipos_salgado
        }
    
    ##================ REMOVER ITENS ========================

    def remover_item(self, id_item, categoria):
        db = dbconnection()

        tabela = "salgados" if categoria == "Salgado" else "bebidas"
        coluna_id = "id_salgado" if categoria == "Salgado" else "id_bebida"

        comando = f"DELETE FROM {tabela} WHERE {coluna_id} = %s;"

        sucesso = db.execute_command(comando, (id_item,))
        db.end_connection()
        return sucesso
    

    ##================ EDITAR PRODUTOS =========================

    def editar_item(self, id_item, categoria, nome, sabor, valor, quantia):
        db = dbconnection()
        tabela = "salgados" if categoria == "Salgado" else "bebidas"
        coluna_id = "id_salgado" if categoria == "Salgado" else "id_bebida"
        
        comando = f"""
            UPDATE {tabela} 
            SET nome = %s, sabor = %s, valor = %s, quantia_estoque = %s 
            WHERE {coluna_id} = %s;
        """
        parametros = (nome, sabor, valor, quantia, id_item)
        
        sucesso = db.execute_command(comando, parametros)
        db.end_connection()
        return sucesso


    ##================ MOVIMENTAÇÃO DE ESTOQUE ==================

    def baixar_estoque(self, id_item, categoria, qtd_desejada):
        db = dbconnection()
        tabela = "salgados" if categoria == "Salgado" else "bebidas"
        coluna_id = "id_salgado" if categoria == "Salgado" else "id_bebida"
        
        check_sql = f"SELECT quantia_estoque FROM {tabela} WHERE {coluna_id} = %s"
        resultado = db.fetch_one(check_sql, (id_item,))
        
        if not resultado or resultado[0] <= 0:
            db.end_connection()
            return 0 
        
        estoque_atual = resultado[0]
        qtd_final = min(qtd_desejada, estoque_atual)
        
        update_sql = f"UPDATE {tabela} SET quantia_estoque = quantia_estoque - %s WHERE {coluna_id} = %s"
        db.execute_command(update_sql, (qtd_final, id_item))
        
        db.end_connection()
        return qtd_final

    ##================ REABASTECIMENTO ===========================

    def listar_fabrica(self):
        db = dbconnection()
        comando = "SELECT nome, sabor, categoria, valor_custo FROM fabrica ORDER BY nome;"
        dados = db.fetch_all(comando)
        db.end_connection()
        
        lista_objetos = []
        for d in dados:
            # d[0]=nome, d[1]=sabor, d[2]=categoria, d[3]=valor_custo
            if d[2] == "Salgado":
                lista_objetos.append(Salgado(0, d[0], d[1], float(d[3]), 0))
            else:
                lista_objetos.append(Bebida(0, d[0], d[1], float(d[3]), 0))
        return lista_objetos

    def comprar_da_fabrica(self, nome, sabor, categoria, quantidade, valor_custo, vendedor_id=None): # Adicionado parâmetro
        db = dbconnection()
        tabela = "salgados" if categoria == "Salgado" else "bebidas"
        custo_total = quantidade * valor_custo

        saldo_disponivel = fin.saldo_atual()
        if custo_total > saldo_disponivel:
            db.end_connection()
            return "saldo_insuficiente"

        comando_estoque = f"""
            UPDATE {tabela} 
            SET quantia_estoque = quantia_estoque + %s 
            WHERE nome = %s AND sabor = %s;
        """
        
        db.cur.execute(comando_estoque, (quantidade, nome, sabor))
        db.conn.commit()
        
        if db.cur.rowcount > 0:
            origem = f"FÁBRICA: {quantidade}x {nome} ({sabor})"
            fin.registrar_movimentacao(origem, custo_total, "SAIDA", vendedor_id=vendedor_id) 
            db.end_connection()
            return True
        else:
            db.end_connection()
            return False