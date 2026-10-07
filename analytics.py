import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import os

conn = sqlite3.connect("database.db")

df = pd.read_sql_query(
    "SELECT category, amount FROM donations",
    conn
)

conn.close()

category_total = df.groupby("category")["amount"].sum()

plt.figure(figsize=(8, 5))

category_total.plot(kind="bar")

plt.title("Donation Amount by Category")
plt.xlabel("Donation Category")
plt.ylabel("Amount (₹)")

plt.tight_layout()

os.makedirs("static/charts", exist_ok=True)

plt.savefig(
    "static/charts/donation_chart.png"
)

plt.close()