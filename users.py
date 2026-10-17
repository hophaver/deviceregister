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
    password_hash = generate_password_hash(password)

    db.execute(
        "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
        (username, password_hash, is_admin),
    )
    return True, None



def authenticate_user(username, password):
    """Authenticate user with username and password. Returns user row if valid, None otherwise."""
    if not username or not password:
        return None

    user = db.query_one(
        "SELECT id, username, password_hash, is_admin FROM users WHERE username = ?",
        (username,),
    )
    if not user:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return user


def get_all_users():
    """Retrieve all registered users ordered alphabetically by username."""
    return db.query("SELECT id, username FROM users ORDER BY username ASC")

