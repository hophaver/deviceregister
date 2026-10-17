"""Device classification queries for categories, types, locations, and operating systems."""

import db


def get_device_types():
    """Retrieve all device types ordered alphabetically."""
    return db.query("SELECT id, name FROM device_types ORDER BY name ASC")


def get_categories():
    """Retrieve all device categories ordered alphabetically."""
    return db.query("SELECT id, name FROM categories ORDER BY name ASC")


def get_locations():
    """Retrieve all locations ordered alphabetically."""
    return db.query("SELECT id, name FROM locations ORDER BY name ASC")


def get_operating_systems():
    """Retrieve all operating systems ordered alphabetically."""
    return db.query("SELECT id, name FROM operating_systems ORDER BY name ASC")


def get_all_classifications():
    """Retrieve all classifications grouped in a dictionary."""
    return {
        "types": get_device_types(),
        "categories": get_categories(),
        "locations": get_locations(),
        "operating_systems": get_operating_systems(),
    }
