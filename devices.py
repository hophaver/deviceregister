import db


def get_all_devices():
    """Retrieve all devices joined with users to include creator and owner usernames."""
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
            c.username AS creator_username,
            o.username AS owner_username
        FROM devices d
        JOIN users c ON d.creator_id = c.id
        LEFT JOIN users o ON d.owner_id = o.id
        ORDER BY d.id DESC
    """
    return db.query(sql)


def search_devices(query_str):
    """Search devices by keyword across names, models, serial numbers, and descriptions."""
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
            c.username AS creator_username,
            o.username AS owner_username
        FROM devices d
        JOIN users c ON d.creator_id = c.id
        LEFT JOIN users o ON d.owner_id = o.id
        WHERE d.name LIKE ?
           OR d.model LIKE ?
           OR d.serial_number LIKE ?
           OR d.description LIKE ?
        ORDER BY d.id DESC
    """
    pattern = f"%{query_str}%"
    return db.query(sql, (pattern, pattern, pattern, pattern))



def validate_device(name, model=None, serial_number=None, description=None):
    """Validate device attributes. Returns (is_valid, error_message)."""
    if not name or not name.strip():
        return False, "Device name is required."
    if len(name.strip()) > 100:
        return False, "Device name cannot exceed 100 characters."
    if model and len(model.strip()) > 100:
        return False, "Model cannot exceed 100 characters."
    if serial_number and len(serial_number.strip()) > 100:
        return False, "Serial number cannot exceed 100 characters."
    if description and len(description.strip()) > 2000:
        return False, "Description cannot exceed 2000 characters."
    return True, None


def create_device(name, model, serial_number, description, creator_id, owner_id):
    """Insert a new device into the database and return its id."""
    cursor = db.execute(
        """
        INSERT INTO devices (name, model, serial_number, description, creator_id, owner_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, model, serial_number, description, creator_id, owner_id),
    )
    return cursor.lastrowid


def get_device_by_id(device_id):
    """Retrieve a single device by its ID with creator and owner usernames."""
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
            c.username AS creator_username,
            o.username AS owner_username
        FROM devices d
        JOIN users c ON d.creator_id = c.id
        LEFT JOIN users o ON d.owner_id = o.id
        WHERE d.id = ?
    """
    return db.query_one(sql, (device_id,))


def update_device(device_id, name, model, serial_number, description, owner_id):
    """Update details of an existing device."""
    db.execute(
        """
        UPDATE devices
        SET name = ?, model = ?, serial_number = ?, description = ?, owner_id = ?
        WHERE id = ?
        """,
        (name, model, serial_number, description, owner_id, device_id),
    )


def delete_device(device_id):
    """Delete a device by its ID."""
    db.execute("DELETE FROM devices WHERE id = ?", (device_id,))




