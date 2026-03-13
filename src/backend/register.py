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

        success = db.execute_command(
            f'INSERT INTO {table} ("user", password) VALUES (%s, %s)',
            (username, hash_password(password))
        )

        if success:
            st.success("Account created! You can now log in.")
        else:
            st.error("Registration failed. Please try again.")
