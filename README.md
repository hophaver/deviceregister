# Device Register

A web-based device inventory and asset register system built for the University of Helsinki course **Tietokannat ja web-ohjelmointi** (Fall 2026).

---

## 1. Application Features

* **User Authentication & Roles**:
  * Visitors can register an account and log in.
  * Passwords are securely hashed with PBKDF2 (`werkzeug.security`).
  * The first registered user automatically receives the **Administrator** role.
* **Granular Privilege Management**:
  * Administrators have full access to manage all devices, classifications, and user accounts.
  * Administrators can add, edit, and delete other users (with self-deletion protection).
  * Administrators can toggle individual user permissions (`can_add`, `can_edit`, `can_delete`).
* **Device Inventory Management**:
  * Users can browse devices with the assigned owner, device type, model, and physical location displayed.
  * Users can create new devices according to their assigned permissions.
  * Device creators and assigned owners can edit and remove their own devices; admins can manage any device.
* **Database-Backed Classifications**:
  * Four independent database classification dimensions:
    * **Device Type** (Laptop, Desktop, Mobile, Server, Network Device, Peripheral, etc.)
    * **Category** (Workstation, Personal, Testing / QA, Infrastructure, Spare, etc.)
    * **Location** (Headquarters, Branch Office, Remote / Home Office, Data Center, etc.)
    * **Operating System** (macOS, Windows, Linux, iOS, Android, Embedded, etc.)
* **Search, Multi-Filtering & Pagination**:
  * Free-text keyword search across device name, model, serial number, and description.
  * Simultaneous multi-attribute dropdown filtering across all classifications.
  * Database-level pagination (`LIMIT` / `OFFSET`) preserving active search and filter queries across page transitions.
* **Maintenance & Service History (Secondary Data Entity)**:
  * Detailed maintenance history log on each device page.
  * Authenticated users can log service events (date, description, cost) for any device.
  * Tracks the servicing technician's username.
* **User Profile & Activity Statistics**:
  * Dedicated profile page for every registered user (`/users/<id>`).
  * Real-time activity statistics: number of devices owned, devices registered, maintenance logs recorded, and total maintenance costs incurred.
  * List of all devices associated with the user (as creator or assigned owner).
* **Security Controls**:
  * Protection against Cross-Site Request Forgery (CSRF) via session token verification on all `POST` forms.
  * Full defense against SQL Injection using strictly parameterized queries (`?`).
  * Route-level authentication and permission enforcement with HTTP 403 / 404 handling.
  * Server-side input validation on usernames, passwords, device fields, and maintenance logs.

---

## 2. Technical Stack

* **Language**: Python 3.10+
* **Framework**: Flask (strictly no other external packages; only Flask and its built-in dependencies such as Werkzeug).
* **Database**: SQLite 3 with raw SQL queries (no ORMs, explicit foreign keys enabled via `PRAGMA foreign_keys = ON;`).
* **Styling**: Minimalist semantic HTML5 (`<label>`, `<input>`, `<table>`) with custom CSS. Completely JavaScript-free.

---

## 3. Installation and Setup

### 3.1 Clone Repository and Enter Directory
```bash
git clone https://github.com/hophaver/deviceregister.git
cd deviceregister
```

### 3.2 Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
*(On Windows: `venv\Scripts\activate`)*

### 3.3 Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.4 Initialize the Database
Creates all tables, constraints, default classifications, and indexes:
```bash
python3 init_db.py
```

### 3.5 Run the Application
```bash
flask run
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

---

## 4. Dataset Seeding & Performance Testing

The project includes a standalone seeding script (`seed.py`) designed to populate the database with a large dataset to stress test performance and verify database indexing:

```bash
python3 seed.py
```

### Seed Data Volume:
* **10 Users** (1 admin + 9 test accounts with passwords `password123`)
* **10,000 Devices** with randomized classifications, models, and serial numbers
* **5,000 Maintenance Records** linked across devices and technicians

### Benchmark Results (10,000+ Devices):
* **Database Generation**: Batch inserted in **~0.20 seconds**.
* **Paginated Listing Load (`LIMIT 10 OFFSET 0`)**: **~9.3 ms**.
* **Full-text Keyword Search across 10,000 rows**: **~4.6 ms**.
* **Multi-Classification Filtering (Type + Location)**: **~1.5 ms**.
* **Device Details with Maintenance History**: **~4.3 ms**.
* **User Profile with Aggregated Activity Statistics**: **~24.2 ms**.

### Database Indexing:
Performance is guaranteed through explicit B-tree indexes defined in `schema.sql`:
* `idx_devices_owner` on `devices(owner_id)`
* `idx_devices_creator` on `devices(creator_id)`
* `idx_devices_name` on `devices(name)`
* `idx_maintenance_device` on `maintenance_logs(device_id)`
* `idx_maintenance_user` on `maintenance_logs(user_id)`

Index usage can be verified using SQLite's query planner:
```sql
EXPLAIN QUERY PLAN SELECT id, name FROM devices WHERE owner_id = 1;
-- SEARCH devices USING INDEX idx_devices_owner (owner_id=?)

EXPLAIN QUERY PLAN SELECT id, description FROM maintenance_logs WHERE device_id = 100;
-- SEARCH maintenance_logs USING INDEX idx_maintenance_device (device_id=?)

EXPLAIN QUERY PLAN SELECT id, name FROM devices WHERE name = 'MacBook Pro 16';
-- SEARCH devices USING COVERING INDEX idx_devices_name (name=?)
```

---

## 5. Code Quality & Pylint

The codebase is audited with `pylint` and achieves a rating of **10.00 / 10**:

```bash
pylint app.py classifications.py db.py devices.py init_db.py maintenance.py seed.py users.py
```

For complete details on module architecture, design decisions, and static analysis results, see [pylint-report.md](pylint-report.md).
