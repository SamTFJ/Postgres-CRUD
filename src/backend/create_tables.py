from src.backend.dbconnection import dbconnection

def init_database():
    db = dbconnection()

    commands = [
        """
        CREATE TABLE IF NOT EXISTS salgados(
            id_salgado SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            sabor VARCHAR(20) NOT NULL default 'Padrão',
            valor DECIMAL(4,2) NOT NULL,
            quantia_estoque SMALLINT NOT NULL default 0
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bebidas(
            id_bebida SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            sabor VARCHAR(20) NOT NULL default 'Padrão',
            valor DECIMAL(5,2) NOT NULL,
            quantia_estoque SMALLINT NOT NULL default 0
        );
        """,
        #enum pra tabela financeiro
        """
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_movimentacao') THEN
                CREATE TYPE tipo_movimentacao AS ENUM ('ENTRADA', 'SAIDA');
            END IF;
        END $$;
        """,
        #tabela de Financeiro
        """
        CREATE TABLE IF NOT EXISTS financeiro (
            id SERIAL PRIMARY KEY,
            origem VARCHAR(100) NOT NULL,
            valor DECIMAL(10, 2) NOT NULL CHECK (valor > 0),
            tipo tipo_movimentacao NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vendedor_id INTEGER REFERENCES credentials_salesman(id) ON DELETE SET NULL,
            cliente_id INTEGER REFERENCES credentials_customer(id) ON DELETE SET NULL
        );
        """,
        #saldo inicial
        """
        INSERT INTO financeiro (origem, valor, tipo)
        SELECT 'Aporte Inicial de Capital', 10000.00, 'ENTRADA'
        WHERE NOT EXISTS (SELECT 1 FROM financeiro);
        """,

        # tabela de Vendas 
        """
        CREATE TABLE IF NOT EXISTS vendas (
            id_venda SERIAL PRIMARY KEY,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            vendedor_id INTEGER REFERENCES credentials_salesman(id) ON DELETE SET NULL,
            cliente_id INTEGER REFERENCES credentials_customer(id) ON DELETE SET NULL,
            valor_total DECIMAL(10,2) NOT NULL
        );
        """,
        # tabela de Itens da Venda 
        """
        CREATE TABLE IF NOT EXISTS itens_venda (
            id_item SERIAL PRIMARY KEY,
            venda_id INTEGER REFERENCES vendas(id_venda) ON DELETE CASCADE,
            produto_nome VARCHAR(50) NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL
        );
        """
        #fabrica para reabastecer estoque
        """
        CREATE TABLE IF NOT EXISTS fabrica (
            id_item_fabrica SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            sabor VARCHAR(20) NOT NULL,
            categoria VARCHAR(10) CHECK (categoria IN ('Salgado', 'Bebida')),
            valor_custo DECIMAL(5,2) NOT NULL
        );
        """

    ]

    print("Criando tabelas...")

    for command in commands:
        success = db.execute_command(command)
        if success:
            print(f"Comando de criação executado!")
        else:
            print(f"Erro ao executar comando!")

    db.end_connection()
    print("Processo finalizado")

if __name__ == "__main__":
    init_database()
