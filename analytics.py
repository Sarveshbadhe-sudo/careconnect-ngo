import sqlite3
import pandas as pd

# Change this to the database file used by Sarvesh
DB_PATH = "database.db"

# Change this if the table name is different
TABLE_NAME = "donations"


def load_donations():
    """Load donation records from SQLite into a Pandas DataFrame."""

    connection = sqlite3.connect(DB_PATH)

    query = f"SELECT * FROM {TABLE_NAME}"

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


def calculate_metrics(df):
    """Calculate overall donation statistics."""

    total_funds = df["amount"].sum()

    average_donation = df["amount"].mean()

    donor_count = len(df)

    return {
        "total_funds": total_funds,
        "average_donation": average_donation,
        "donor_count": donor_count
    }


def category_totals(df):
    """Calculate total funds collected for each category."""

    result = (
        df.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return result


def payment_method_distribution(df):
    """Count donations according to payment method."""

    result = df["payment_method"].value_counts()

    return result


def get_dashboard_data():
    """Return all analytics required by the dashboard."""

    df = load_donations()

    metrics = calculate_metrics(df)

    categories = category_totals(df)

    payment_methods = payment_method_distribution(df)

    return df, metrics, categories, payment_methods


if __name__ == "__main__":

    df, metrics, categories, payment_methods = get_dashboard_data()

    print("\n===== DONATION ANALYTICS =====")

    print("\nTotal Funds Collected:",
          metrics["total_funds"])

    print("Average Donation:",
          round(metrics["average_donation"], 2))

    print("Total Donor Count:",
          metrics["donor_count"])

    print("\n===== CATEGORY-WISE TOTALS =====")
    print(categories)

    print("\n===== PAYMENT METHOD DISTRIBUTION =====")
    print(payment_methods)