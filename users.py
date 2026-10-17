import db
from werkzeug.security import check_password_hash, generate_password_hash


def validate_registration(username, password):
    """Validate registration parameters. Returns (is_valid, error_message)."""
    if not username:
        return False, "Username is required."
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters."
    if not password:
        return False, "Password is required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."
    if len(password) > 100:
        return False, "Password cannot exceed 100 characters."
    return True, None


def register_user(username, password):
    """Register a new user. The first registered user is automatically made admin."""
    is_valid, error = validate_registration(username, password)
    if not is_valid:
        return False, error

    existing_user = db.query_one(
        "SELECT id FROM users WHERE username = ?",
        (username,),
    )
    if existing_user:
        return False, "Username is already taken."

    count_row = db.query_one("SELECT COUNT(id) AS count FROM users")
    is_admin = 1 if count_row["count"] == 0 else 0
    can_add = 1
    can_edit = 1
    can_delete = 1 if is_admin else 0
    password_hash = generate_password_hash(password)

    db.execute(
        "INSERT INTO users (username, password_hash, is_admin, can_add, can_edit, can_delete) VALUES (?, ?, ?, ?, ?, ?)",
        (username, password_hash, is_admin, can_add, can_edit, can_delete),
    )
    return True, None


def authenticate_user(username, password):
    """Authenticate user with username and password. Returns user row if valid, None otherwise."""
    if not username or not password:
        return None

    user = db.query_one(
        "SELECT id, username, password_hash, is_admin, can_add, can_edit, can_delete FROM users WHERE username = ?",
        (username,),
    )
    if not user:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return user


def get_user_privileges(user_id):
    """Retrieve user privileges. Admins automatically have all permissions."""
    row = db.query_one(
        "SELECT is_admin, can_add, can_edit, can_delete FROM users WHERE id = ?",
        (user_id,),
    )
    if not row:
        return None
    is_admin = bool(row["is_admin"])
    return {
        "is_admin": is_admin,
        "can_add": is_admin or bool(row["can_add"]),
        "can_edit": is_admin or bool(row["can_edit"]),
        "can_delete": is_admin or bool(row["can_delete"]),
    }


def update_user_privileges(user_id, can_add, can_edit, can_delete):
    """Update privilege flags for a given user."""
    db.execute(
        "UPDATE users SET can_add = ?, can_edit = ?, can_delete = ? WHERE id = ?",
        (int(bool(can_add)), int(bool(can_edit)), int(bool(can_delete)), user_id),
    )


def get_all_users():
    """Retrieve all registered users with details and privileges."""
    return db.query(
        "SELECT id, username, is_admin, can_add, can_edit, can_delete, created_at FROM users ORDER BY username ASC"
    )


def delete_user(user_id):
    """Delete a user account and clean up their device references."""
    db.execute("UPDATE devices SET owner_id = NULL WHERE owner_id = ?", (user_id,))
    db.execute("DELETE FROM devices WHERE creator_id = ?", (user_id,))
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))


def get_user_by_id(user_id):
    """Retrieve user details by ID."""
    return db.query_one(
        """
        SELECT id, username, is_admin, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    )


def get_devices_by_user(user_id):
    """Retrieve all devices owned or created by a user."""
    sql = """
        SELECT
            d.id,
            d.name,
            d.model,
            d.serial_number,
            d.description,
            d.creator_id,
            d.owner_id,
            d.created_at,
            t.name AS type_name,
            loc.name AS location_name
        FROM devices d
        LEFT JOIN device_types t ON d.type_id = t.id
        LEFT JOIN locations loc ON d.location_id = loc.id
        WHERE d.owner_id = ? OR d.creator_id = ?
        ORDER BY d.id DESC
    """
    return db.query(sql, (user_id, user_id))




