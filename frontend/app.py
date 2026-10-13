import streamlit as st
import os
import requests
from dotenv import load_dotenv
from view_expenses_ui import view_expenses_tab
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab

# Load environment variables
load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("Expenses Tracking System")

if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    login_tab, signup_tab = st.tabs(["Login", "Sign up"])

    with login_tab:
        with st.form("login_form"):
            login_username = st.text_input("Username")
            login_password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Login")
        if login_submitted:
            response = requests.post(
                f"{API_URL}/auth/login",
                json={"username": login_username, "password": login_password},
            )
            if response.status_code == 200:
                session = response.json()
                st.session_state.token = session["token"]
                st.session_state.username = session["username"]
                st.rerun()
            else:
                st.error(response.json().get("detail", "Login failed"))

    with signup_tab:
        with st.form("signup_form"):
            signup_username = st.text_input("Username", key="signup_username")
            signup_password = st.text_input("Password", type="password", key="signup_password")
            signup_confirmation = st.text_input("Confirm password", type="password")
            signup_submitted = st.form_submit_button("Create account")
        if signup_submitted:
            if signup_password != signup_confirmation:
                st.error("Passwords do not match")
            else:
                response = requests.post(
                    f"{API_URL}/auth/signup",
                    json={"username": signup_username, "password": signup_password},
                )
                if response.status_code == 200:
                    session = response.json()
                    st.session_state.token = session["token"]
                    st.session_state.username = session["username"]
                    st.rerun()
                else:
                    st.error(response.json().get("detail", "Signup failed"))
    st.stop()

username = st.session_state.username
headers = {"Authorization": f"Bearer {st.session_state.token}"}
st.sidebar.write(f"Signed in as **{username}**")
if st.sidebar.button("Log out"):
    st.session_state.token = None
    st.session_state.pop("username", None)
    st.rerun()

tab1, tab2, tab3 = st.tabs(["View Expenses", "Add/Update", "Analytics"])

with tab1:
    view_expenses_tab(headers)

with tab2:
    add_update_tab(headers)

with tab3:
    analytics_tab(headers)