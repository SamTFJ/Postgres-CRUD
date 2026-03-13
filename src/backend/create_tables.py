from src.backend.dbconnection import dbconnection

def init_database():
    db = dbconnection()

    commands = [
        """
        CREATE TABLE IF NOT EXISTS salgados(
            id_salgado SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            valor DECIMAL(4,2) NOT NULL,
            quantia_estoque SMALLINT,
            sabor VARCHAR(20)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS bebidas(
            id_bebida SERIAL PRIMARY KEY,
            nome VARCHAR(30) NOT NULL,
            valor DECIMAL(5,2) NOT NULL,
            quantia_estoque SMALLINT,
            sabor VARCHAR(20),
            volume_ml SMALLINT
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
