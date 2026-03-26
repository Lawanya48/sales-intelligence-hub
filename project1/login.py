import streamlit as st
import pandas as pd
import db_connection

st.title("Login")

conn = db_connection.connect_db()

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):

    query = """
    SELECT username, role, branch_id
    FROM users
    WHERE username=%s AND password=%s
    """

    cursor = conn.cursor()
    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:

        st.session_state["logged_in"] = True
        st.session_state["username"] = result[0]
        st.session_state["role"] = result[1]
        st.session_state["branch_id"] = result[2]

        st.success("Login successful")

        st.switch_page("pages/dashboard.py")

    else:
        st.error("Invalid username or password")