import streamlit as st
import time
import hashlib
from .dbconnection import dbconnection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(db: dbconnection, username: str, password: str, table: str) -> bool:
    result = db.fetch_one(
        f'SELECT password FROM {table} WHERE "user" = %s',
        (username,)
    )
    if result is None:
        return False
    return result[0] == hash_password(password)

def login(type, function, table):
    if 'valid1' not in st.session_state:
        st.session_state.valid1 = False

    if 'valid2' not in st.session_state:
        st.session_state.valid2 = False

    titles = {1: "Client Log-in", 2: "Salesman Log-in"}
    state_keys = {1: "valid1", 2: "valid2"}

    state_key = state_keys[type]

    if not st.session_state[state_key]:
        st.title(titles[type])

        username = st.text_input("Username", key=f"login_user_{type}")
        password = st.text_input("Password", type="password", key=f"login_pass_{type}")

        if st.button("Enter", key=f"login_btn_{type}"):
            db = dbconnection()
            if check_credentials(db, username, password, table):
                st.session_state[state_key] = True
                st.success("Logging in...!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Wrong login information!")
    else:
        function()