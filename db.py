import sqlite3
from flask import g

DATABASE = "database.db"


def get_db():
    """Retrieve or open database connection for current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close database connection on request teardown."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    """Register database teardown handler with Flask app."""
    app.teardown_appcontext(close_db)


def query(sql, params=()):
    """Execute a SELECT query and return all rows."""
    cursor = get_db().execute(sql, params)
    return cursor.fetchall()


def query_one(sql, params=()):
    """Execute a SELECT query and return a single row or None."""
    cursor = get_db().execute(sql, params)
    return cursor.fetchone()


def execute(sql, params=()):
    """Execute a write query (INSERT/UPDATE/DELETE) and commit transaction."""
    db = get_db()
    cursor = db.execute(sql, params)
    db.commit()
    return cursor
