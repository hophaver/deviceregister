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
