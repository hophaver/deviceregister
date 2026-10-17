"""Database schema initialization and seed script for default classifications."""

import sqlite3

DATABASE = "database.db"

DEFAULT_DEVICE_TYPES = [
    "Laptop",
    "Desktop",
    "Mobile",
    "Server",
    "Network Device",
    "Peripheral",
    "Other",
]

DEFAULT_CATEGORIES = [
    "Workstation",
    "Personal",
    "Testing / QA",
    "Infrastructure",
    "Spare / Storage",
]

DEFAULT_LOCATIONS = [
    "Headquarters (HQ)",
    "Branch Office",
    "Remote / Home Office",
    "Data Center",
    "Storage Room",
]

DEFAULT_OPERATING_SYSTEMS = [
    "macOS",
    "Windows",
    "Linux",
    "iOS",
    "Android",
    "Embedded / None",
    "Other",
]


def init_db():
    """Create database tables from schema.sql and populate default classifications."""
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # Insert default classifications
    conn.executemany(
        "INSERT INTO device_types (name) VALUES (?)",
        [(name,) for name in DEFAULT_DEVICE_TYPES],
    )
    conn.executemany(
        "INSERT INTO categories (name) VALUES (?)",
        [(name,) for name in DEFAULT_CATEGORIES],
    )
    conn.executemany(
        "INSERT INTO locations (name) VALUES (?)",
        [(name,) for name in DEFAULT_LOCATIONS],
    )
    conn.executemany(
        "INSERT INTO operating_systems (name) VALUES (?)",
        [(name,) for name in DEFAULT_OPERATING_SYSTEMS],
    )

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
