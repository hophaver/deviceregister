import db
from werkzeug.security import check_password_hash, generate_password_hash


def register_user(username, password):
    """Register a new user. The first registered user is automatically made admin."""
    if not username or not password:
        return False, "Username and password are required."

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
