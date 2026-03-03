import sqlite3

DB_NAME = "electricity_ai.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Slab Configuration Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS slab_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            min_units INTEGER,
            max_units INTEGER,
            rate_per_unit REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Billing Settings Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            fixed_charge_per_kw REAL,
            sanctioned_load REAL,
            surcharge_percent REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Bills Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            month INTEGER,
            year INTEGER,
            units_consumed REAL,
            energy_charges REAL,
            fixed_charges REAL,
            ed_surcharge REAL,
            total_grid_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, month, year),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()