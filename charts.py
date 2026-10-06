import matplotlib.pyplot as plt
from pathlib import Path

from analytics import load_donations, category_totals, payment_method_distribution


# Folder where charts will be saved
CHART_FOLDER = Path("static/images/charts")

# Create folder automatically
CHART_FOLDER.mkdir(parents=True, exist_ok=True)


def generate_category_chart(df):
    """Generate bar chart for category-wise funds."""

    data = category_totals(df)

    plt.figure(figsize=(8, 5))

    data.plot(kind="bar")

    plt.title("Funds Raised Per Category")
    plt.xlabel("Donation Category")
    plt.ylabel("Funds Collected")

    plt.xticks(rotation=0)

    plt.tight_layout()

    file_path = CHART_FOLDER / "category_funds.png"

    plt.savefig(file_path, dpi=150)

    plt.close()

    return str(file_path)


def generate_payment_chart(df):
    """Generate pie chart for payment methods."""

    data = payment_method_distribution(df)

    plt.figure(figsize=(7, 7))

    plt.pie(
        data.values,
        labels=data.index,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Payment Method Distribution")

    plt.tight_layout()

    file_path = CHART_FOLDER / "payment_methods.png"

    plt.savefig(file_path, dpi=150)

    plt.close()

    return str(file_path)


def generate_all_charts():
    """Generate all dashboard charts."""

    df = load_donations()

    category_chart = generate_category_chart(df)

    payment_chart = generate_payment_chart(df)

    return category_chart, payment_chart


if __name__ == "__main__":

    category_chart, payment_chart = generate_all_charts()

    print("Charts generated successfully!")

    print("Category chart:",
          category_chart)

    print("Payment chart:",
          payment_chart)