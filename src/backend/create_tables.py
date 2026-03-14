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
        """,
        #=======VIEWS=============
        #junta salgados e bebidas em uma lista so
        """
        CREATE OR REPLACE VIEW vw_estoque_geral AS
        SELECT id_salgado AS id, nome, sabor, valor, quantia_estoque, 'Salgado' AS categoria 
        FROM salgados
        UNION ALL
        SELECT id_bebida AS id, nome, sabor, valor, quantia_estoque, 'Bebida' AS categoria 
        FROM bebidas;
        """,

        #estoque critico (itens abaixo de 5 unidades)
        """
        CREATE OR REPLACE VIEW vw_estoque_critico AS
        SELECT * FROM vw_estoque_geral WHERE quantia_estoque < 5
        ORDER BY quantia_estoque DESC;
        """

        #relatorio financeiro
        """
        CREATE OR REPLACE VIEW vw_financeiro_detalhado AS
        SELECT 
            f.id,
            f.data_hora,
            f.origem,
            f.valor,
            f.tipo,
            COALESCE(c.user, 'Consumidor Final') AS nome_cliente,
            COALESCE(s.user, 'Vendedor/Sistema') AS nome_vendedor
        FROM financeiro f
        LEFT JOIN credentials_customer c ON f.cliente_id = c.id
        LEFT JOIN credentials_salesman s ON f.vendedor_id = s.id;
        """,

        #itens q mais foram vendidos
        """
        CREATE OR REPLACE VIEW vw_ranking_vendas AS
        SELECT 
            produto_nome, 
            SUM(quantidade) AS total_vendido, 
            SUM(quantidade * preco_unitario) AS faturamento_total
        FROM itens_venda
        GROUP BY produto_nome
        ORDER BY total_vendido DESC;
        """

    ]

    print("Configurando tabelas e views...")

    for command in commands:
        success = db.execute_command(command)
        if not success:
            print(f"Erro ao executar comando!")

    db.end_connection()
    print("Processo finalizado com sucesso")

if __name__ == "__main__":
    init_database()
