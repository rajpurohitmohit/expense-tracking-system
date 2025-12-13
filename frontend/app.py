import streamlit as st
import os
from dotenv import load_dotenv
from view_expenses_ui import view_expenses_tab
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("Expenses Tracking System")

tab1, tab2, tab3 = st.tabs(["View Expenses", "Add/Update", "Analytics"])

with tab1:
    view_expenses_tab()

with tab2:
    add_update_tab()

with tab3:
    analytics_tab()