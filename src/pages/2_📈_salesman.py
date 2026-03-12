import streamlit as st
from pathlib import Path
import sys

root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
from src.backend.register import register

st.set_page_config(
    page_title="Salesman Menu",
    page_icon="📊"
)

def helloworld():
    st.write("hello world!")

if not st.session_state.get("valid2", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=2, function=helloworld, table="credentials_salesman")

    with tab_register:
        register(table="credentials_salesman")
else:
    login(type=2, function=helloworld, table="credentials_salesman")