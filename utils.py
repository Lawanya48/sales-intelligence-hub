import pandas as pd

# LOAD CSV FILES
def load_data():
    branches = pd.read_csv("data/branches.csv")
    sales = pd.read_csv("data/customer_sales.csv")
    payments = pd.read_csv("data/payment_splits.csv")
    users = pd.read_csv("data/users.csv")

    return branches, sales, payments, users


# SAVE DATA
def save_data(sales, payments):
    sales.to_csv("data/customer_sales.csv", index=False)
    payments.to_csv("data/payment_splits.csv", index=False)


# TRIGGER LOGIC
def update_received_amount(sales, payments):

    received = payments.groupby("sale_id")["amount_paid"].sum().reset_index()
    received.columns = ["sale_id", "received_amount"]

    sales = sales.drop(columns=["received_amount"], errors="ignore")
    sales = sales.merge(received, on="sale_id", how="left")

    sales["received_amount"] = sales["received_amount"].fillna(0)
    sales["pending_amount"] = sales["gross_sales"] - sales["received_amount"]

    return sales