import streamlit as st
import pandas as pd
import db_connection

st.title("📊 Sales Dashboard")

# 🔐 Login check
if not st.session_state.get("login"):
    st.warning("Please login first")
    st.stop()

# 🔴 Navigation
page = st.sidebar.radio("Go to", ["Dashboard", "Add Customer", "Queries"])

if page == "Add Customer":
    st.switch_page("pages/add_customer.py")

if page == "Queries":
    st.switch_page("pages/queries.py")

# 🔹 Load data
branches, sales, payments, users = db_connection.load_data()

# 🔹 Convert numeric columns
sales["gross_sales"] = pd.to_numeric(sales["gross_sales"], errors="coerce")
sales["received_amount"] = pd.to_numeric(sales["received_amount"], errors="coerce")
sales["pending_amount"] = pd.to_numeric(sales["pending_amount"], errors="coerce")

# 🔹 Merge branch name
sales = sales.merge(branches, on="branch_id")

# 🔹 Convert date
sales["date"] = pd.to_datetime(sales["date"], dayfirst=True, errors="coerce")

# 🔹 Keep original copy
sales_full = sales.copy()

# 🔹 Role info
role = st.session_state["role"]
branch_id = st.session_state["branch_id"]

# ================= FILTERS =================

st.sidebar.header("🔍 Filters")

# 👑 Branch filter
if role == "Super Admin":
    branch_filter = st.sidebar.selectbox(
        "Branch",
        ["All"] + list(sales_full["branch_name"].unique())
    )

    if branch_filter != "All":
        sales = sales_full[sales_full["branch_name"] == branch_filter]
    else:
        sales = sales_full.copy()

else:
    # Admin restriction
    sales = sales_full[sales_full["branch_id"] == branch_id]

# 🔹 Course filter
course_filter = st.sidebar.selectbox(
    "Course",
    ["All"] + list(sales["product_name"].unique())
)

if course_filter != "All":
    sales = sales[sales["product_name"] == course_filter]

# 🔹 Date range filter
date_range = st.sidebar.date_input("📅 Select Date Range", [])

if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    sales = sales[
        (sales["date"] >= start_date) &
        (sales["date"] <= end_date)
    ]

# ================= SUMMARY =================

st.subheader("📊 Summary")

st.write("💰 Total Gross:", sales["gross_sales"].sum())
st.write("✅ Received:", sales["received_amount"].sum())
st.write("⏳ Pending:", sales["pending_amount"].sum())

# ================= BRANCH SUMMARY =================

st.subheader("🏢 Branch Summary")

branch_summary = sales.groupby("branch_name").agg({
    "gross_sales": "sum",
    "received_amount": "sum",
    "pending_amount": "sum"
}).reset_index()

if branch_summary.empty:
    st.warning("No data available ❌")
else:
    st.dataframe(branch_summary)

# ================= RECORDS =================

st.subheader("📋 Records")

# ✅ ALWAYS SHOW FILTERED DATA
st.dataframe(sales)

# ================= ADD PAYMENT =================

st.subheader("➕ Add Payment")

sale_id = st.text_input("Enter Sale ID")
amount = st.number_input("Amount Paid", min_value=0.0)
method = st.selectbox("Payment Method", ["Cash", "UPI", "Card"])

if st.button("Add Payment"):

    if sale_id.strip() == "":
        st.error("Enter Sale ID ❌")

    elif not sale_id.isdigit():
        st.error("Sale ID must be number ❌")

    else:
        sale_id = int(sale_id)

        if sale_id not in sales_full["sale_id"].values:
            st.error("Sale ID not found ❌")

        else:
            sale_record = sales_full[sales_full["sale_id"] == sale_id]

            if role == "Admin" and sale_record.iloc[0]["branch_id"] != branch_id:
                st.error("This Sale ID does not belong to your branch ❌")

            else:
                new_payment = pd.DataFrame({
                    "sale_id": [sale_id],
                    "amount_paid": [amount],
                    "payment_method": [method]
                })

                payments = pd.concat([payments, new_payment], ignore_index=True)
                db_connection.save_payment(payments)

                st.success("Payment Added Successfully ✅")

                # Reload updated data
                branches, sales, payments, users = db_connection.load_data()
                sales = sales.merge(branches, on="branch_id")

                updated = sales[sales["sale_id"] == sale_id]

                st.subheader("✅ Updated Record")
                st.dataframe(updated)

# ================= LOGOUT =================

if st.button("Logout"):
    st.session_state.clear()
    st.switch_page("login.py")