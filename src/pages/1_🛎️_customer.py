import streamlit as st
from pathlib import Path
import sys

root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
from src.backend.register import register

st.set_page_config(
    page_title="Customer Menu",
    page_icon="🛎️"
)

def helloworld():
    st.write("hello world!")

if not st.session_state.get("valid1", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=1, function=helloworld, table="credentials_customer")

    with tab_register:
        register(table="credentials_customer")
else:
    login(type=1, function=helloworld, table="credentials_customer")