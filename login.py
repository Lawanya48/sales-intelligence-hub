import streamlit as st
import db_connection

st.title("🔐 Sales Intelligence Hub Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

branches, sales, payments, users = db_connection.load_data()

if st.button("Login"):
    user = users[
        (users["username"] == username) &
        (users["password"] == password)
    ]

    if not user.empty:
        st.session_state["login"] = True
        st.session_state["role"] = user.iloc[0]["role"]
        st.session_state["branch_id"] = user.iloc[0]["branch_id"]

        st.success("Login Successful ✅")
        st.switch_page("pages/dashboard.py")
    else:
        st.error("Invalid Credentials ❌")