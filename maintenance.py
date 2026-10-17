"""Maintenance log service layer handling device service history and submissions."""

import db


def get_logs_for_device(device_id):
    """Retrieve all maintenance logs for a specific device ordered newest first."""
    sql = """
        SELECT
            m.id,
            m.device_id,
            m.user_id,
            m.service_date,
            m.description,
            m.cost,
            m.created_at,
            u.username AS technician_username
        FROM maintenance_logs m
        JOIN users u ON m.user_id = u.id
        WHERE m.device_id = ?
        ORDER BY m.service_date DESC, m.id DESC
    """
    return db.query(sql, (device_id,))


def add_maintenance_log(device_id, user_id, service_date, description, cost=0.0):
    """Insert a new maintenance log record."""
    cursor = db.execute(
        """
        INSERT INTO maintenance_logs (device_id, user_id, service_date, description, cost)
        VALUES (?, ?, ?, ?, ?)
        """,
        (device_id, user_id, service_date, description, cost),
    )
    return cursor.lastrowid
