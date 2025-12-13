import streamlit as st
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def view_expenses_tab():
    response = requests.get(f"{API_URL}/expenses/")

    if (response.status_code == 200):
        expenses = response.json()
        st.dataframe(expenses)
    else:
        st.error("Failed to retrieve expenses!")
        expenses =[]