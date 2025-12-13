import streamlit as st
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def add_update_tab():
    selected_date = st.date_input("Enter Date", datetime(2025, 1, 2), label_visibility="collapsed")
    response = requests.get(f"{API_URL}/expenses/{selected_date}")     

    if (response.status_code == 200):
        expenses = response.json() 
    else:
        st.error("Failed to retrieve expenses!")
        expenses = []

    categories = ["Rent", "Food", "Shopping", "Entertainment", "Other"]
    with st.form(key="expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.text("Amount")

        with col2:
            st.text("Category")

        with col3:
            st.text("Notes")


        for i in range(5):
            if i < len(expenses):
                amount = expenses[i]['amount']
                category = expenses[i]['category']
                notes = expenses[i]['notes']
            else:
                amount = 0.0
                category = 'Rent'
                notes = ""

            col1, col2, col3 = st.columns(3) 

            with col1:
                amount_input = st.number_input(label="Amount", min_value=0.0, step=1.0, value=amount, key=f"amount_{selected_date}_{i}", label_visibility="collapsed")

            with col2:
                category_input = st.selectbox(label="Category", options=categories,index=categories.index(category), key=f"category_{selected_date}_{i}", label_visibility="collapsed") 

            with col3:
                notes_input = st.text_input(label="Notes", value=notes, key=f"notes_{selected_date}_{i}", label_visibility="collapsed")

        submit_button = st.form_submit_button()


        if(submit_button):
            expenses_for_submit = []

            for i in range(5):
                amount = st.session_state[f"amount_{selected_date}_{i}"]
                category = st.session_state[f"category_{selected_date}_{i}"] 
                notes = st.session_state[f"notes_{selected_date}_{i}"]

                if amount > 0:
                    expenses_for_submit.append({
                        "amount": amount,
                        "category": category,
                        "notes": notes
                    })

            response = requests.post(url=f"{API_URL}/expenses/{selected_date}", json=expenses_for_submit)
            if response.status_code == 200:
                st.success("Expense Updated Successfully!")
            else:
                message = response.json()
                st.error(message.get('message', 'Error updating expenses'))
