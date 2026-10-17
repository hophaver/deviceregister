"""
Dataset Seeding Script for Device Register.
Generates 10,000+ devices, multiple users, and maintenance records for stress testing.
"""

import random
import sqlite3
import time
from werkzeug.security import generate_password_hash
import init_db

DATABASE = "database.db"
DEVICE_COUNT = 10000
LOG_COUNT = 5000

SAMPLE_DEVICE_NAMES = [
    "MacBook Pro 16",
    "MacBook Pro 14",
    "MacBook Air 13",
    "ThinkPad X1 Carbon",
    "ThinkPad T14s",
    "Dell XPS 15",
    "Dell Latitude 5540",
    "HP EliteBook 840",
    "Apple iPad Pro 12.9",
    "Apple iPhone 15 Pro",
    "Samsung Galaxy S24",
    "Google Pixel 8",
    "Dell PowerEdge R750",
    "HP ProLiant DL380",
    "Cisco Catalyst 9300",
    "Ubiquiti UniFi Switch 48",
    "Synology DiskStation DS923+",
    "LG UltraFine 27 Monitor",
    "Dell UltraSharp 32 Monitor",
    "Logitech MX Master 3S",
]

SAMPLE_MODELS = [
    "M3 Max",
    "M3 Pro",
    "M2",
    "Gen 11",
    "Gen 4",
    "9530",
    "G10",
    "2024 Edition",
    "Enterprise",
    "Pro Edition",
]

SAMPLE_LOG_DESCRIPTIONS = [
    "Routine annual inspection and cleaning",
    "Battery replacement and battery health calibration",
    "Keyboard replacement due to sticky key mechanism",
    "Screen replacement after minor drop damage",
    "Thermal paste replacement and heatsink dusting",
    "SSD storage upgrade to 2TB NVMe",
    "RAM expansion to 64GB DDR5",
    "OS reinstallation and security hardening",
    "Diagnostic check on power supply unit",
    "Firmware update and port connectivity test",
]


def seed_database():
    start_time = time.time()
    print("Reinitializing database schema and default classifications...")
    init_db.init_db()

    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")

    # 1. Seed users
    print("Seeding users...")
    password_hash = generate_password_hash("password123")
    user_data = [
        ("admin", password_hash, 1, 1, 1, 1),
        ("alice", password_hash, 0, 1, 1, 0),
        ("bob", password_hash, 0, 1, 1, 0),
        ("charlie", password_hash, 0, 1, 1, 1),
        ("diana", password_hash, 0, 1, 1, 0),
        ("eric", password_hash, 0, 1, 1, 0),
        ("fiona", password_hash, 0, 1, 1, 1),
        ("george", password_hash, 0, 1, 1, 0),
        ("helen", password_hash, 0, 1, 1, 0),
        ("ian", password_hash, 0, 1, 1, 0),
    ]
    conn.executemany(
        """
        INSERT INTO users (username, password_hash, is_admin, can_add, can_edit, can_delete)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        user_data,
    )
    conn.commit()

    user_ids = [row[0] for row in conn.execute("SELECT id FROM users").fetchall()]
    type_ids = [row[0] for row in conn.execute("SELECT id FROM device_types").fetchall()]
    category_ids = [row[0] for row in conn.execute("SELECT id FROM categories").fetchall()]
    location_ids = [row[0] for row in conn.execute("SELECT id FROM locations").fetchall()]
    os_ids = [row[0] for row in conn.execute("SELECT id FROM operating_systems").fetchall()]

    # 2. Seed 10,000+ devices in batch
    print(f"Generating and inserting {DEVICE_COUNT:,} devices...")
    device_rows = []
    for i in range(1, DEVICE_COUNT + 1):
        name = random.choice(SAMPLE_DEVICE_NAMES)
        model = random.choice(SAMPLE_MODELS)
        serial_number = f"SN-{random.randint(100000, 999999)}-{i:05d}"
        description = f"Inventory unit #{i:05d}. Standard corporate issue asset."
        type_id = random.choice(type_ids)
        category_id = random.choice(category_ids)
        location_id = random.choice(location_ids)
        os_id = random.choice(os_ids)
        creator_id = random.choice(user_ids)
        owner_id = random.choice(user_ids) if random.random() > 0.1 else None

        device_rows.append((
            name, model, serial_number, description,
            type_id, category_id, location_id, os_id,
            creator_id, owner_id
        ))

    conn.executemany(
        """
        INSERT INTO devices (
            name, model, serial_number, description,
            type_id, category_id, location_id, os_id,
            creator_id, owner_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        device_rows,
    )
    conn.commit()

    device_ids = [row[0] for row in conn.execute("SELECT id FROM devices").fetchall()]

    # 3. Seed maintenance logs in batch
    print(f"Generating and inserting {LOG_COUNT:,} maintenance logs...")
    log_rows = []
    for _ in range(LOG_COUNT):
        dev_id = random.choice(device_ids)
        tech_id = random.choice(user_ids)
        service_date = f"2026-{random.randint(1, 10):02d}-{random.randint(1, 28):02d}"
        description = random.choice(SAMPLE_LOG_DESCRIPTIONS)
        cost = round(random.uniform(15.0, 450.0), 2)
        log_rows.append((dev_id, tech_id, service_date, description, cost))

    conn.executemany(
        """
        INSERT INTO maintenance_logs (device_id, user_id, service_date, description, cost)
        VALUES (?, ?, ?, ?, ?)
        """,
        log_rows,
    )
    conn.commit()
    conn.close()

    elapsed = time.time() - start_time
    print("=" * 50)
    print("Seeding completed successfully!")
    print(f"Total time elapsed: {elapsed:.2f} seconds")
    print(f"Users created:      {len(user_ids)}")
    print(f"Devices created:    {len(device_rows):,}")
    print(f"Maintenance logs:   {len(log_rows):,}")
    print("=" * 50)


if __name__ == "__main__":
    seed_database()
