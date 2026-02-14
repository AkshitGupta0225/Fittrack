import streamlit as st
from db import get_user, create_user, verify_password


def show_auth():
    st.title("Welcome to FitTrack Pro+")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = get_user(username)
            if user and verify_password(password, user["password_hash"]):
                st.session_state.user = {
                    "id": user["id"],
                    "username": user["username"]
                }
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            create_user(new_user, new_pass)
            st.success("Account created")
