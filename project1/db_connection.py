import mysql.connector

def connect_db():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Software@5",
        database="sales_hub"
    )

    return conn