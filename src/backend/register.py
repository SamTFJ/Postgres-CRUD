import streamlit as st
import hashlib
from .dbconnection import dbconnection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register(table: str):
    st.title("Register")

    username = st.text_input("Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pass")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

    #inicia variaveis pra n ter erro de referencia
    time_coracao = None
    assiste_one_piece = False
    cidade = ""

    #campo cliente

    if table == "credentials_customer":
        st.divider()
        st.info("Preencha os campos abaixo para liberar descontos especiais!")
        time_coracao = st.text_input("Qual seu time do coração?", placeholder="Ex: Flamengo, Vasco da Gama", key="reg_time")  
        assiste_one_piece = st.selectbox(
            "Você assiste One Piece?", 
            options=[True, False], 
            format_func=lambda x: "Sim" if x else "Não",
            key="reg_op"
        )
        cidade = st.text_input("Em qual cidade você mora?", placeholder="Ex: João Pessoa, Sousa", key="reg_cidade")


    if st.button("Register", key="reg_btn"):
        if not username or not password:
            st.error("Username and password are required.")
            return

        if password != confirm:
            st.error("Passwords do not match.")
            return

        db = dbconnection()

        existing = db.fetch_one(
            f'SELECT id FROM {table} WHERE "user" = %s',
            (username,)
        )
        if existing:
            st.error("Username already taken.")
            return

       # Lógica de inserção baseada na tabela
        try:
            # hash da senha uma única vez para usar nos comandos abaixo
            senha_criptografada = hash_password(password)

            if table == "credentials_customer":
                #  cliente
                sql = f'INSERT INTO {table} ("user", password, time_coracao, assiste_one_piece, cidade) VALUES (%s, %s, %s, %s, %s)'
                params = (username, senha_criptografada, time_coracao, assiste_one_piece, cidade)
            else:
                #  vendedores 
                sql = f'INSERT INTO {table} ("user", password) VALUES (%s, %s)'
                params = (username, senha_criptografada)

            success = db.execute_command(sql, params)

            if success:
                st.success("Account created! You can now log in.")
            else:
                st.error("Registration failed. Please try again.")

        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
        finally:
            db.end_connection()
