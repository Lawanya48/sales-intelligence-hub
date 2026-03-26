import streamlit as st
import pandas as pd
import db_connection

st.title("➕ Add New Customer")

# 🔐 Check login
if not st.session_state.get("login"):
    st.warning("Please login first")
    st.stop()

branches, sales, payments, users = db_connection.load_data()

role = st.session_state["role"]
session_branch_id = st.session_state["branch_id"]

# ================= FORM =================

with st.form("customer_form"):

    # 👑 Super Admin → select branch
    if role == "Super Admin":
        branch_id = st.selectbox(
            "Select Branch",
            branches["branch_id"]
        )
    else:
        # 👤 Admin → auto assign branch
        branch_id = session_branch_id
        st.write(f"Branch ID: {branch_id} (Auto Assigned)")

    date = st.date_input("Date")
    name = st.text_input("Customer Name")
    mobile = st.text_input("Mobile Number")
    course = st.selectbox("Course", ["DS", "DA", "BA", "FSD"])
    gross = st.number_input("Gross Sales", min_value=0.0)

    submit = st.form_submit_button("Add Customer")

    if submit:

        # 🔹 Auto generate sale_id
        if len(sales) == 0:
            new_id = 1
        else:
            new_id = int(sales["sale_id"].max()) + 1

        # 🔹 Create new row
        new_row = pd.DataFrame({
            "sale_id": [new_id],
            "branch_id": [branch_id],
            "date": [date],
            "name": [name],
            "mobile_number": [mobile],
            "product_name": [course],
            "gross_sales": [gross],
            "status": ["Open"]
        })

        # 🔹 Save
        sales = pd.concat([sales, new_row], ignore_index=True)
        db_connection.save_sales(sales)

        st.success(f"Customer Added Successfully ✅ (Sale ID: {new_id})")