# Biblioteca para conectar com o PostgreSQL
import psycopg2
from psycopg2 import sql
# Biblioteca para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv
# Importa o módulo 'os' para interagir com o sistema operacional e pegar as variáveis
import os
# Biblioteca para comandos assíncronos
import asyncio

# Carrega as variáveis do arquivo .env
load_dotenv(".env",override = True)

class dbconnection:
    def __init__(self):
        # Inicializa os atributos como None para evitar erros caso a conexão falhe
        self.conn = None
        self.cur = None

        # Tenta estabelecer a conexão com o banco de dados
        try:
            self.conn = psycopg2.connect(
                dbname= os.getenv("db_name"),
                user=os.getenv("db_user"),
                password=os.getenv("db_password"),
                host=os.getenv("db_host"),
                port=os.getenv("db_port")
            )
        
        except (Exception, psycopg2.Error) as error:
            print("\n--> Error while connecting to PostgreSQL: ", error)

        # Tenta criar um cursor para executar comandos SQL
        try:
            self.cur = self.conn.cursor()

        except psycopg2.Error as error:
            print("\n--> Couldn't create the cursor")

    # Encerrar as conexões com o banco de dados
    def end_connection(self):
        self.cur.close()
        self.conn.close()

    # Executa um comando de SQL (INSERT, UPDATE, DELETE)
    def execute_command(self, sqlcommand, Params = None):
        try:
            self.cur.execute(sqlcommand, Params)
            # Confirma (salva) as alterações feitas no banco de dados
            self.conn.commit()
            return True
        except (Exception, psycopg2.Error) as error:
            print("\n--> Command Execution Error: ", error)
            self.conn.rollback() # Desfaz a operação em caso de erro
            return False
        
    # Busca um único resultado de uma query SELECT
    def fetch_one(self, sqlcommand, Params = None):
        try:
            self.cur.execute(sqlcommand, Params)
            return self.cur.fetchone()
        except (Exception, psycopg2.Error) as error:
            print("\n--> Searching Data Error:", error)
            return None
        
    # Método para BUSCAR TODOS os resultados de uma query SELECT
    def fetch_all(self, sqlcommand, Params=None):
        try:
            self.cur.execute(sqlcommand, Params)
            return self.cur.fetchall()
        except (Exception, psycopg2.Error) as error:
            print("\n--> Searching Data Error: ", error)
            return [] # Retorna uma lista vazia em caso de erro

# Este bloco só é executado se você rodar diretamente (para testes de conexão!)
if __name__ == "__main__":
    db = dbconnection()

    # Exemplo de query para listar todas as tabelas
    query = sql.SQL("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

    # Exemplo de query que busca dados
    query2 = sql.SQL("""SELECT * FROM item;""")

    db.execute_command(query2)
    for item in db.cur.fetchall():
        print("+-------+")
        for items in item:
            if items == item[0]:
                print("|", items, "   |")
            else:
                print("|", items, "|")

    db.end_connection()