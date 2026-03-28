# Biblioteca para conectar com o PostgreSQL
import psycopg2
from psycopg2 import sql
# Biblioteca para carregar variáveis de ambiente de um arquivo .env
from dotenv import load_dotenv
# Importa o módulo 'os' para interagir com o sistema operacional e pegar as variáveis
import os
# Para conectar com o Supabase
from supabase import create_client, Client
import streamlit as st

# Carrega as variáveis do arquivo .env
load_dotenv(".env",override = True)

class dbconnection:
    def __init__(self):
        # Inicializa os atributos como None
        self.supabase: Client = None
        self.conn = None
        self.cur = None

        # 1. Tenta carregar as variáveis de ambiente do .env primeiro
        load_dotenv(".env", override=True)
        
        url = os.getenv("supabase_url")
        key = os.getenv("supabase_key")
        db_url = os.getenv("supabase_db_url")

        # 2. Se não encontrou no .env, tenta pegar do Streamlit Secrets
        if not url or not key or not db_url:
            try:
                # Se estiver rodando via Streamlit Cloud
                url = st.secrets["supabase_url"]
                key = st.secrets["supabase_key"]
                db_url = st.secrets["supabase_db_url"]
            except Exception:
                # Se chegar aqui e ainda não tiver os dados, vai dar erro na conexão abaixo
                pass

        # 3. Estabelece a conexão
        try:
            if url and key:
                self.supabase = create_client(url, key)
            
            if db_url:
                self.conn = psycopg2.connect(db_url)
                self.cur = self.conn.cursor()
            else:
                print("\n--> Erro Crítico: Nenhuma credencial de banco de dados encontrada!")

        except (Exception, psycopg2.Error) as error:
            print("\n--> Error while connecting to Database: ", error)

    # Encerrar as conexões com o banco de dados
    def end_connection(self):
        if self.cur:
            self.cur.close()
        if self.conn:
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

    db.execute_command(query)
    for item in db.cur.fetchall():
        print("+---------------+")
        for items in item:
            if items == item[0]:
                print("|", items, "   |")
            else:
                print("|", items, "|")

    db.end_connection()