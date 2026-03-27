import streamlit as st
import time
import hashlib
from .dbconnection import dbconnection

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(db: dbconnection, username: str, password: str, table: str):
    result = db.fetch_one(
        f'SELECT id, password FROM {table} WHERE "user" = %s',
        (username,)
    )
    if result is None:
        return None
    user_id, stored_password = result
    if stored_password == hash_password(password):
        return user_id
    return None

def login(type, function, table):
    if 'valid1' not in st.session_state:
        st.session_state.valid1 = False

    if 'valid2' not in st.session_state:
        st.session_state.valid2 = False

    titles = {1: "Client Log-in", 2: "Salesman Log-in"}
    state_keys = {1: "valid1", 2: "valid2"}
    id_keys = {1: "user_id", 2: "salesman_id"}

    state_key = state_keys[type]
    id_key = id_keys[type]

    if not st.session_state[state_key]:
        st.title(titles[type])

        username = st.text_input("Username", key=f"login_user_{type}")
        password = st.text_input("Password", type="password", key=f"login_pass_{type}")

        if st.button("Enter", key=f"login_btn_{type}"):
            db = dbconnection()
            user_id = check_credentials(db, username, password, table)
            if user_id is not None:
                st.session_state[state_key] = True
                st.session_state[id_key] = user_id
                st.success("Logging in...!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Wrong login information!")
    else:
        function()