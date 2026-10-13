import streamlit as st
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def view_expenses_tab(headers):
    st.subheader("Your Expenses")
    if st.button("Refresh expenses"):
        st.rerun()

    response = requests.get(f"{API_URL}/expenses", headers=headers, timeout=10)

    if (response.status_code == 200):
        expenses = response.json()
        st.dataframe(expenses)
    else:
        st.error("Failed to retrieve expenses!")
        expenses =[]