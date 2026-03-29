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
            produto_sabor VARCHAR(50) NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario DECIMAL(10,2) NOT NULL
        );
        """,
        # local_fabricacao direto nas tabelas de produtos (default Mari para produtos já cadastrados)
        """
        ALTER TABLE salgados ADD COLUMN IF NOT EXISTS local_fabricacao VARCHAR(30) NOT NULL DEFAULT 'Mari';
        """,
        """
        ALTER TABLE bebidas ADD COLUMN IF NOT EXISTS local_fabricacao VARCHAR(30) NOT NULL DEFAULT 'Mari';
        """,
        # colunas de pagamento em vendas (podem já existir)
        """
        ALTER TABLE vendas ADD COLUMN IF NOT EXISTS metodo_pagamento VARCHAR(20);
        """,
        """
        ALTER TABLE vendas ADD COLUMN IF NOT EXISTS status_pagamento VARCHAR(20) DEFAULT 'Confirmado';
        """,
        #fabrica para reabastecer estoque
        """
        CREATE TABLE IF NOT EXISTS fabrica (
            id_item_fabrica SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            sabor VARCHAR(20) NOT NULL,
            categoria VARCHAR(10) CHECK (categoria IN ('Salgado', 'Bebida')),
            valor_custo DECIMAL(5,2) NOT NULL,
            local_fabricacao VARCHAR(30) NOT NULL DEFAULT 'Mari'
        );
        """,
        # coluna de local_fabricacao caso tabela ja exista
        """
        ALTER TABLE fabrica ADD COLUMN IF NOT EXISTS local_fabricacao VARCHAR(30) NOT NULL DEFAULT 'Mari';
        """,
        #=======VIEWS=============
        # drop das views dependentes antes de recriar (evita erro de mudança de tipo de coluna)
        "DROP VIEW IF EXISTS vw_estoque_critico;",
        "DROP VIEW IF EXISTS vw_estoque_geral;",
        #junta salgados e bebidas em uma lista so
        """
        CREATE OR REPLACE VIEW vw_estoque_geral AS
        SELECT id_salgado AS id, nome, sabor, valor, quantia_estoque, 'Salgado' AS categoria, local_fabricacao
        FROM salgados
        UNION ALL
        SELECT id_bebida AS id, nome, sabor, valor, quantia_estoque, 'Bebida' AS categoria, local_fabricacao
        FROM bebidas;
        """,

        #estoque critico (itens abaixo de 5 unidades)
        """
        CREATE OR REPLACE VIEW vw_estoque_critico AS
        SELECT * FROM vw_estoque_geral WHERE quantia_estoque < 5
        ORDER BY quantia_estoque DESC;
        """,

        #relatorio financeiro
        """
        CREATE OR REPLACE VIEW vw_financeiro_detalhado AS
        SELECT 
            f.id,
            f.data_hora,
            f.origem,
            f.valor,
            f.tipo,
            COALESCE(v.status_pagamento, 'Confirmado') AS status_pagamento,
            COALESCE(c.user, 'Fabrica/Reabastecer') AS nome_cliente,
            COALESCE(s.user, 'Vendedor/Sistema') AS nome_vendedor
        FROM financeiro f
        LEFT JOIN credentials_customer c ON f.cliente_id = c.id
        LEFT JOIN credentials_salesman s ON f.vendedor_id = s.id
        LEFT JOIN vendas v ON (f.origem LIKE 'Venda #%') 
            AND (v.id_venda = NULLIF(regexp_replace(f.origem, '\\D', '', 'g'), '')::INT);
                """,

        #itens q mais foram vendidos
        """
        CREATE OR REPLACE VIEW vw_ranking_vendas AS
        SELECT 
            produto_nome, 
            SUM(quantidade) AS total_vendido, 
            SUM(quantidade * preco_unitario) AS faturamento_total
        FROM itens_venda
        GROUP BY produto_nome, produto_sabor
        ORDER BY total_vendido DESC;
        """,
        # verificar dados e pedidos do cliente
        """
        CREATE OR REPLACE VIEW vw_historico_pedidos AS
        SELECT
            v.id_venda,
            v.cliente_id,
            c."user" AS nome_cliente,
            v.data_hora,
            v.valor_total,
            string_agg(i.produto_nome || ' (' || i.produto_sabor || ') x' || i.quantidade, ', ') AS detalhe_itens
        FROM vendas v
        LEFT JOIN credentials_customer c ON v.cliente_id = c.id
        JOIN itens_venda i ON v.id_venda = i.venda_id
        GROUP BY v.id_venda, v.cliente_id, c."user", v.data_hora, v.valor_total
        ORDER BY v.data_hora DESC;
        """,

        # relatorio mensal de vendas agrupado por vendedor e mes
        """
        CREATE OR REPLACE VIEW vw_relatorio_mensal_vendedor AS
        SELECT
            COALESCE(cs."user", 'Sem Vendedor') AS vendedor,
            TO_CHAR(DATE_TRUNC('month', v.data_hora), 'MM/YYYY') AS mes,
            DATE_TRUNC('month', v.data_hora) AS mes_ordenacao,
            COUNT(v.id_venda) AS total_vendas,
            SUM(v.valor_total) AS faturamento_total,
            AVG(v.valor_total) AS ticket_medio
        FROM vendas v
        LEFT JOIN credentials_salesman cs ON v.vendedor_id = cs.id
        GROUP BY cs."user", DATE_TRUNC('month', v.data_hora)
        ORDER BY mes_ordenacao DESC, faturamento_total DESC;
        """,

        #=======STORED PROCEDURE=============
        # procedure atomica para registrar uma venda completa (venda + itens + financeiro)
        """
        CREATE OR REPLACE PROCEDURE sp_registrar_venda(
            p_valor_total       DECIMAL(10,2),
            p_cliente_id        INTEGER,
            p_vendedor_id       INTEGER,
            p_metodo_pagamento  VARCHAR(20),
            p_status_pagamento  VARCHAR(20),
            p_itens             JSONB
        )
        LANGUAGE plpgsql AS $$
        DECLARE
            v_id_venda INTEGER;
            v_item     JSONB;
        BEGIN
            INSERT INTO vendas (valor_total, cliente_id, vendedor_id, metodo_pagamento, status_pagamento)
            VALUES (p_valor_total, p_cliente_id, p_vendedor_id, p_metodo_pagamento, p_status_pagamento)
            RETURNING id_venda INTO v_id_venda;

            FOR v_item IN SELECT * FROM jsonb_array_elements(p_itens)
            LOOP
                INSERT INTO itens_venda (venda_id, produto_nome, produto_sabor, quantidade, preco_unitario)
                VALUES (
                    v_id_venda,
                    v_item->>'nome',
                    v_item->>'sabor',
                    (v_item->>'qtd')::INTEGER,
                    (v_item->>'preco_unitario')::DECIMAL
                );
            END LOOP;

            INSERT INTO financeiro (origem, valor, tipo, cliente_id, vendedor_id)
            VALUES (
                'Venda #' || v_id_venda || ' (' || p_metodo_pagamento || ')',
                p_valor_total,
                'ENTRADA',
                p_cliente_id,
                p_vendedor_id
            );
        END;
        $$;
        """,

        #=======ÍNDICES=============
        # aceleram buscas frequentes por cliente, vendedor, produto e data
        "CREATE INDEX IF NOT EXISTS idx_vendas_cliente   ON vendas(cliente_id);",
        "CREATE INDEX IF NOT EXISTS idx_vendas_vendedor  ON vendas(vendedor_id);",
        "CREATE INDEX IF NOT EXISTS idx_vendas_data      ON vendas(data_hora);",
        "CREATE INDEX IF NOT EXISTS idx_itens_venda      ON itens_venda(venda_id);",
        "CREATE INDEX IF NOT EXISTS idx_itens_produto    ON itens_venda(produto_nome);",
        "CREATE INDEX IF NOT EXISTS idx_financeiro_tipo  ON financeiro(tipo);",
        "CREATE INDEX IF NOT EXISTS idx_financeiro_data  ON financeiro(data_hora);",
        "CREATE INDEX IF NOT EXISTS idx_salgados_nome    ON salgados(nome);",
        "CREATE INDEX IF NOT EXISTS idx_bebidas_nome     ON bebidas(nome);",

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
