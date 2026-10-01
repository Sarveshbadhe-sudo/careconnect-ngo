import sqlite3

DB_NAME = "ngo_donations.db"

def get_db_connection():
    """Establishes a connection to the SQLite database with row-access by column name."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables and seeds initial test data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table (M1 / M2: Data Input and Storage)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'donor'
    );
    """)

    # 2. Donations Table (M1 / M2: Normalized donation entries)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        donor_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        payment_mode TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (donor_id) REFERENCES users (id)
    );
    """)

    # Seed Default NGO Admin Account
    cursor.execute("""
    INSERT OR IGNORE INTO users (id, name, email, password, role)
    VALUES (1, 'Admin Leena', 'admin@ashrayseva.org', 'admin123', 'admin');
    """)

    # Seed Initial Donors for testing
    cursor.execute("""
    INSERT OR IGNORE INTO users (id, name, email, password, role)
    VALUES (2, 'Ramesh Patil', 'ramesh@gmail.com', 'pass123', 'donor');
    """)

    cursor.execute("""
    INSERT OR IGNORE INTO users (id, name, email, password, role)
    VALUES (3, 'Anita Sharma', 'anita@gmail.com', 'pass123', 'donor');
    """)

    # Seed Initial Donation Data (M6 Testing Requirement)
    cursor.execute("""
    INSERT OR IGNORE INTO donations (id, donor_id, amount, category, payment_mode, notes)
    VALUES 
    (1, 2, 5000.0, 'Healthcare & Medicine', 'UPI', 'Monthly medical support for elders'),
    (2, 3, 2500.0, 'Daily Meals & Groceries', 'Net Banking', 'Ration contribution'),
    (3, 2, 10000.0, 'Shelter Upkeep', 'Card', 'Winter blanket & geyser maintenance');
    """)

    conn.commit()
    conn.close()
    print("Database and tables initialized with seed records.")

# Helper queries for the web routes
def register_user(name, email, password, role='donor'):
    """Inserts a new donor into the database."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (name, email, password, role)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Email already exists
    finally:
        conn.close()

def record_donation(donor_id, amount, category, payment_mode, notes=""):
    """Inserts a new donation entry with validation."""
    if float(amount) <= 0:
        return False
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO donations (donor_id, amount, category, payment_mode, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (donor_id, float(amount), category, payment_mode, notes)
    )
    conn.commit()
    conn.close()
    return True

if __name__ == '__main__':
    init_db()
    # Quick self-test
    test_reg = register_user("Test Donor", "donor_test@example.com", "pass123")
    print(f"User registration test passed: {test_reg}")
    
    test_don = record_donation(donor_id=2, amount=1500, category="Healthcare & Medicine", payment_mode="UPI", notes="Verification check")
    print(f"Donation record test passed: {test_don}")