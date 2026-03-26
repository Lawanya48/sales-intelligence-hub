import streamlit as st
import pandas as pd
import db_connection

st.title("🧠 SQL Queries (Using Pandas)")

# 🔐 Login check
if not st.session_state.get("login"):
    st.warning("Please login first")
    st.stop()

# Load data
branches, sales, payments, users = db_connection.load_data()

# Convert numeric
sales["gross_sales"] = pd.to_numeric(sales["gross_sales"], errors="coerce")
sales["received_amount"] = pd.to_numeric(sales["received_amount"], errors="coerce")
sales["pending_amount"] = pd.to_numeric(sales["pending_amount"], errors="coerce")

# Convert date
sales["date"] = pd.to_datetime(sales["date"], dayfirst=True, errors="coerce")

# Merge for joins
sales_branch = sales.merge(branches, on="branch_id")

# ================= SELECT QUERY ================= #

category = st.selectbox("Select Category", [
    "Basic Queries",
    "Aggregation Queries",
    "Join Queries",
    "Financial Queries"
])

# ================= BASIC ================= #

if category == "Basic Queries":

    query = st.selectbox("Choose Query", [
        "All Customer Sales",
        "All Branches",
        "All Payments",
        "Open Sales",
        "Chennai Branch Sales"
    ])

    if query == "All Customer Sales":
        st.dataframe(sales)

    elif query == "All Branches":
        st.dataframe(branches)

    elif query == "All Payments":
        st.dataframe(payments)

    elif query == "Open Sales":
        st.dataframe(sales[sales["status"] == "Open"])

    elif query == "Chennai Branch Sales":
        result = sales_branch[sales_branch["branch_name"] == "Chennai"]
        st.dataframe(result)

# ================= AGGREGATION ================= #

elif category == "Aggregation Queries":

    query = st.selectbox("Choose Query", [
        "Total Gross Sales",
        "Total Received Amount",
        "Total Pending Amount",
        "Sales Count per Branch",
        "Average Sales"
    ])

    if query == "Total Gross Sales":
        st.write(sales["gross_sales"].sum())

    elif query == "Total Received Amount":
        st.write(sales["received_amount"].sum())

    elif query == "Total Pending Amount":
        st.write(sales["pending_amount"].sum())

    elif query == "Sales Count per Branch":
        result = sales_branch.groupby("branch_name").size().reset_index(name="count")
        st.dataframe(result)

    elif query == "Average Sales":
        st.write(sales["gross_sales"].mean())

# ================= JOIN ================= #

elif category == "Join Queries":

    query = st.selectbox("Choose Query", [
        "Sales with Branch Name",
        "Sales with Total Payment",
        "Branch-wise Total Sales",
        "Sales with Payment Method",
        "Sales with Branch Admin"
    ])

    if query == "Sales with Branch Name":
        st.dataframe(sales_branch)

    elif query == "Sales with Total Payment":
        payment_sum = payments.groupby("sale_id")["amount_paid"].sum().reset_index()
        result = sales.merge(payment_sum, on="sale_id", how="left")
        st.dataframe(result)

    elif query == "Branch-wise Total Sales":
        result = sales_branch.groupby("branch_name")["gross_sales"].sum().reset_index()
        st.dataframe(result)

    elif query == "Sales with Payment Method":
        result = sales.merge(payments, on="sale_id", how="left")
        st.dataframe(result)

    elif query == "Sales with Branch Admin":
        result = sales_branch[["sale_id", "branch_name", "branch_admin_name"]]
        st.dataframe(result)

# ================= FINANCIAL ================= #

elif category == "Financial Queries":

    query = st.selectbox("Choose Query", [
        "Pending > 5000",
        "Top 3 Sales",
        "Highest Branch Sales",
        "Monthly Sales",
        "Payment Method Total"
    ])

    if query == "Pending > 5000":
        st.dataframe(sales[sales["pending_amount"] > 5000])

    elif query == "Top 3 Sales":
        st.dataframe(sales.nlargest(3, "gross_sales"))

    elif query == "Highest Branch Sales":
        result = sales_branch.groupby("branch_name")["gross_sales"].sum().reset_index()
        st.dataframe(result.sort_values(by="gross_sales", ascending=False).head(1))

    elif query == "Monthly Sales":
        sales["month"] = sales["date"].dt.to_period("M")
        result = sales.groupby("month")["gross_sales"].sum().reset_index()
        st.dataframe(result)

    elif query == "Payment Method Total":
        result = payments.groupby("payment_method")["amount_paid"].sum().reset_index()
        st.dataframe(result)

# ================= BACK ================= #

if st.button("⬅ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")