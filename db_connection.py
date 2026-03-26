import pandas as pd

def load_data():
    branches = pd.read_csv("data/branches.csv")
    sales = pd.read_csv("data/customer_sales.csv")
    payments = pd.read_csv("data/payment_splits.csv")
    users = pd.read_csv("data/users.csv")

    # 🔥 Trigger logic
    received = payments.groupby("sale_id")["amount_paid"].sum().reset_index()
    received.columns = ["sale_id", "received_amount"]

    sales = sales.drop(columns=["received_amount"], errors="ignore")
    sales = sales.merge(received, on="sale_id", how="left")

    sales["received_amount"] = sales["received_amount"].fillna(0)
    sales["pending_amount"] = sales["gross_sales"] - sales["received_amount"]

    return branches, sales, payments, users


def save_payment(payments):
    payments.to_csv("data/payment_splits.csv", index=False)


def save_sales(sales):
    sales.to_csv("data/customer_sales.csv", index=False)