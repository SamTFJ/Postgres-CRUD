from src.backend.dbconnection import dbconnection

def init_database():
    db = dbconnection()

    commands = [
        """
        CREATE TABLE IF NOT EXISTS salgados(
            id_salgado SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            valor DECIMAL(4,2) NOT NULL,
            quantia_estoque SMALLINT NOT NULL default 0,
            sabor VARCHAR(20) NOT NULL default 'Padrão'
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bebidas(
            id_bebida SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            valor DECIMAL(5,2) NOT NULL,
            quantia_estoque SMALLINT NOT NULL default 0,
            sabor VARCHAR(20) NOT NULL default 'Padrão',
            volume_ml SMALLINT default 100
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
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        #saldo inicial
        """
        INSERT INTO financeiro (origem, valor, tipo)
        SELECT 'Aporte Inicial de Capital', 10000.00, 'ENTRADA'
        WHERE NOT EXISTS (SELECT 1 FROM financeiro);
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
