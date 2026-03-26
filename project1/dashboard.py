import streamlit as st
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from db_connection import connect_db



# Check login
if "logged_in" not in st.session_state:
    st.warning("Please login first")
    st.stop()

st.title("Sales Intelligence Hub Dashboard")

conn = connect_db()
cursor = conn.cursor()

role = st.session_state["role"]
branch_id = st.session_state["branch_id"]
username = st.session_state["username"]

# Show logged user
st.success(f"Logged in as: {username}")

# ---------------------------
# Show sales records
# ---------------------------

if role == "Super Admin":
    query = "SELECT * FROM customer_sales"
else:
    query = f"SELECT * FROM customer_sales WHERE branch_id = {branch_id}"

df = pd.read_sql(query, conn)

st.subheader("📋 Customer / Student Sales Details")
st.dataframe(df)

st.divider()

# ---------------------------
# Payment Section
# ---------------------------

st.subheader("💳 Customer Payment")

sale_id = st.text_input("Enter Sale ID")

pending_amount = None
if role == "Super Admin":
    fetch_query = """
    SELECT name, mobile_number, product_name, gross_sales, received_amount
    FROM customer_sales
    WHERE sale_id = %s
    """

    cursor.execute(fetch_query, (sale_id,))
    result = cursor.fetchone()
    if result:

        name = result[0]
        mobile = result[1]
        product = result[2]
        gross_sales = result[3]
        received_amount = result[4]

        pending_amount = gross_sales - received_amount

        st.write("### Customer Details")
        st.write("Name:", name)
        st.write("Mobile:", mobile)
        st.write("Product:", product)
        st.write("Total Amount:", gross_sales)
        st.write("Received Amount:", received_amount)

        st.info(f"Pending Amount: ₹ {pending_amount}")

    else:
        st.error("Sale ID not found")


elif sale_id and branch_id:

    fetch_query = """
    SELECT name, mobile_number, product_name, gross_sales, received_amount
    FROM customer_sales
    WHERE sale_id = %s AND branch_id = %s
    """

    cursor.execute(fetch_query, (sale_id, branch_id))
    result = cursor.fetchone()

    if result:

        name = result[0]
        mobile = result[1]
        product = result[2]
        gross_sales = result[3]
        received_amount = result[4]

        pending_amount = gross_sales - received_amount

        st.write("### Customer Details")
        st.write("Name:", name)
        st.write("Mobile:", mobile)
        st.write("Product:", product)
        st.write("Total Amount:", gross_sales)
        st.write("Received Amount:", received_amount)

        st.info(f"Pending Amount: ₹ {pending_amount}")

    else:
        st.error("Sale ID not found")

# Payment input
payment_amount = st.number_input("Enter Payment Amount", min_value=0.0)

if st.button("Pay"):

    if not sale_id:
        st.error("Enter Sale ID")

    elif payment_amount <= 0:
        st.error("Enter valid payment amount")

    else:

        update_query = """
        UPDATE customer_sales
        SET received_amount = received_amount + %s
        WHERE sale_id = %s
        """

        cursor.execute(update_query, (payment_amount, sale_id))
        conn.commit()

        # Get updated amount
        cursor.execute("""
        SELECT gross_sales, received_amount
        FROM customer_sales
        WHERE sale_id = %s
        """, (sale_id,))

        updated = cursor.fetchone()

        remaining = updated[0] - updated[1]

        st.success("Payment Successful ✅")
        st.info(f"Remaining Amount: ₹ {remaining}")

        #refresh table
        query1 = "SELECT * FROM customer_sales WHERE sale_id = %s"
        df = pd.read_sql(query1, conn, params=(sale_id,))
        st.dataframe(df)

        st.title("Sales Intelligence Hub Dashboard")

col1, col2 = st.columns([8,1])

with col2:
    if st.button(" Logout "):
        st.session_state.clear()
        st.switch_page("login.py")