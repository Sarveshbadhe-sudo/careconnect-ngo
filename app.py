from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "donation_management_secret_key"

DATABASE = "database.db"


# ---------------- DATABASE CONNECTION ----------------

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- DATABASE INITIALIZATION ----------------

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'donor'
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_name TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin"))

            return redirect(url_for("donate"))

        flash("Invalid email or password")

    return render_template("login.html")


# ---------------- REGISTRATION ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        try:
            conn.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, "donor")
            )

            conn.commit()
            flash("Registration successful. Please login.")

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            flash("Email already registered.")

        finally:
            conn.close()

    return render_template("register.html")


# ---------------- DONATION PORTAL ----------------

@app.route("/donate", methods=["GET", "POST"])
def donate():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "donor":
        return redirect(url_for("admin"))

    if request.method == "POST":

        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]

        conn = get_db_connection()

        conn.execute(
            """
            INSERT INTO donations
            (donor_name, category, amount, date)
            VALUES (?, ?, ?, ?)
            """,
            (session["name"], category, amount, date)
        )

        conn.commit()
        conn.close()

        flash("Donation submitted successfully!")

        return redirect(url_for("donate"))

    return render_template(
        "donate.html",
        name=session["name"]
    )


# ---------------- ADMIN DASHBOARD ----------------

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        return redirect(url_for("donate"))

    conn = get_db_connection()

    donations = conn.execute(
        "SELECT * FROM donations ORDER BY id DESC"
    ).fetchall()

    total_donations = conn.execute(
        "SELECT COUNT(*) FROM donations"
    ).fetchone()[0]

    total_amount = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM donations"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        donations=donations,
        total_donations=total_donations,
        total_amount=total_amount
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- MAIN ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)