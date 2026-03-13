import streamlit as st
from pathlib import Path
import sys

root_dir = str(Path(__file__).parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.backend.login import login
from src.backend.register import register


st.set_page_config(
    page_title="Vendedor",
    page_icon="📊"
)

def menu_vendedor():
     st.subheader("🧑‍💼 Menu Vendedor")



if not st.session_state.get("valid2", False):
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login(type=2, function=menu_vendedor, table="credentials_salesman")

    with tab_register:
        register(table="credentials_salesman")
else:
    login(type=2, function=menu_vendedor, table="credentials_salesman")