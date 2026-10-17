"""Flask application for Device Register inventory management system."""

import os
import secrets
from flask import Flask, render_template, request, redirect, session, abort
import db
import users
import devices
import classifications
import maintenance

app = Flask(__name__)
app.secret_key = os.urandom(24)
db.init_app(app)

PAGE_SIZE = 10


def _parse_filter_args(args):
    """Extract and cast search and classification query parameters."""
    def _int_or_none(key):
        val = args.get(key, "").strip()
        return int(val) if val else None

    return {
        "query": args.get("query", "").strip(),
        "type_id": _int_or_none("type_id"),
        "category_id": _int_or_none("category_id"),
        "location_id": _int_or_none("location_id"),
        "os_id": _int_or_none("os_id"),
    }


def _parse_device_form(form):
    """Parse and clean form data for device creation and updates."""
    def _int_or_none(key):
        val = form.get(key, "").strip()
        return int(val) if val else None

    return {
        "name": form.get("name", "").strip(),
        "model": form.get("model", "").strip() or None,
        "serial_number": form.get("serial_number", "").strip() or None,
        "description": form.get("description", "").strip() or None,
        "owner_id": _int_or_none("owner_id"),
        "type_id": _int_or_none("type_id"),
        "category_id": _int_or_none("category_id"),
        "location_id": _int_or_none("location_id"),
        "os_id": _int_or_none("os_id"),
    }


@app.before_request
def csrf_protect():
    """Enforce CSRF token verification on all state-changing POST requests."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    if request.method == "POST":
        token = request.form.get("csrf_token")
        if not token or token != session.get("csrf_token"):
            abort(403)


@app.route("/")
def index():
    """Render the device listing page with search, filters, and pagination."""
    f = _parse_filter_args(request.args)
    page_str = request.args.get("page", "1").strip()
    try:
        page = max(1, int(page_str))
    except ValueError:
        page = 1

    total_devices = devices.count_filtered_devices(
        keyword=f["query"],
        type_id=f["type_id"],
        category_id=f["category_id"],
        location_id=f["location_id"],
        os_id=f["os_id"],
    )
    total_pages = max(1, (total_devices + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    offset = (page - 1) * PAGE_SIZE

    device_list = devices.get_filtered_devices(
        keyword=f["query"],
        type_id=f["type_id"],
        category_id=f["category_id"],
        location_id=f["location_id"],
        os_id=f["os_id"],
        limit=PAGE_SIZE,
        offset=offset,
    )

    all_classifications = classifications.get_all_classifications()
    user_id = session.get("user_id")
    privileges = users.get_user_privileges(user_id) if user_id else None
    can_add = bool(privileges and privileges["can_add"])

    return render_template(
        "index.html",
        devices=device_list,
        query=f["query"],
        type_id=f["type_id"],
        category_id=f["category_id"],
        location_id=f["location_id"],
        os_id=f["os_id"],
        classifications=all_classifications,
        can_add=can_add,
        page=page,
        total_pages=total_pages,
        total_devices=total_devices,
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("register.html", error="Username and password are required.")

        success, error = users.register_user(username, password)
        if not success:
            return render_template("register.html", error=error)

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user authentication and session establishment."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("login.html", error="Username and password are required.")

        user = users.authenticate_user(username, password)
        if not user:
            return render_template("login.html", error="Invalid username or password.")

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["is_admin"] = bool(user["is_admin"])
        return redirect("/")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    """Terminate the current user session."""
    session.clear()
    return redirect("/")


@app.route("/devices/new", methods=["GET", "POST"])
def new_device():
    """Render and handle the new device registration form."""
    if "user_id" not in session:
        return redirect("/login")

    privileges = users.get_user_privileges(session["user_id"])
    if not privileges or not privileges["can_add"]:
        abort(403)

    all_users = users.get_all_users()
    all_classifications = classifications.get_all_classifications()

    if request.method == "POST":
        d = _parse_device_form(request.form)
        is_valid, error = devices.validate_device(
            d["name"], d["model"], d["serial_number"], d["description"]
        )
        if not is_valid:
            return render_template(
                "new_device.html",
                users=all_users,
                classifications=all_classifications,
                error=error,
            )

        devices.create_device(
            d["name"],
            d["model"],
            d["serial_number"],
            d["description"],
            session["user_id"],
            d["owner_id"],
            type_id=d["type_id"],
            category_id=d["category_id"],
            location_id=d["location_id"],
            os_id=d["os_id"],
        )
        return redirect("/")

    return render_template(
        "new_device.html", users=all_users, classifications=all_classifications
    )


@app.route("/devices/<int:device_id>")
def device_details(device_id):
    """Display comprehensive details and maintenance history for a device."""
    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session.get("user_id")
    privileges = users.get_user_privileges(user_id) if user_id else None
    is_owner_or_creator = bool(
        user_id and user_id in (device["creator_id"], device["owner_id"])
    )
    can_edit = bool(
        privileges
        and (privileges["is_admin"] or (is_owner_or_creator and privileges["can_edit"]))
    )
    can_delete = bool(
        privileges
        and (privileges["is_admin"] or (is_owner_or_creator and privileges["can_delete"]))
    )

    device_logs = maintenance.get_logs_for_device(device_id)

    return render_template(
        "device.html",
        device=device,
        can_edit=can_edit,
        can_delete=can_delete,
        maintenance_logs=device_logs,
    )


@app.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
def edit_device(device_id):
    """Render and handle the device editing form."""
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    privileges = users.get_user_privileges(user_id)
    if not privileges:
        abort(403)

    is_owner_or_creator = user_id in (device["creator_id"], device["owner_id"])
    if not privileges["is_admin"] and not (is_owner_or_creator and privileges["can_edit"]):
        abort(403)

    all_users = users.get_all_users()
    all_classifications = classifications.get_all_classifications()

    if request.method == "POST":
        d = _parse_device_form(request.form)
        is_valid, error = devices.validate_device(
            d["name"], d["model"], d["serial_number"], d["description"]
        )
        if not is_valid:
            return render_template(
                "edit_device.html",
                device=device,
                users=all_users,
                classifications=all_classifications,
                error=error,
            )

        devices.update_device(
            device_id,
            d["name"],
            d["model"],
            d["serial_number"],
            d["description"],
            d["owner_id"],
            type_id=d["type_id"],
            category_id=d["category_id"],
            location_id=d["location_id"],
            os_id=d["os_id"],
        )
        return redirect(f"/devices/{device_id}")

    return render_template(
        "edit_device.html",
        device=device,
        users=all_users,
        classifications=all_classifications,
    )


@app.route("/devices/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    """Handle device deletion if the user is authorized."""
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    privileges = users.get_user_privileges(user_id)
    if not privileges:
        abort(403)

    is_owner_or_creator = user_id in (device["creator_id"], device["owner_id"])
    if not privileges["is_admin"] and not (is_owner_or_creator and privileges["can_delete"]):
        abort(403)

    devices.delete_device(device_id)
    return redirect("/")


@app.route("/devices/<int:device_id>/maintenance", methods=["POST"])
def add_maintenance_log(device_id):
    """Record a maintenance log entry for a device."""
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    service_date = request.form.get("service_date", "").strip()
    description = request.form.get("description", "").strip()
    cost_str = request.form.get("cost", "").strip()

    try:
        cost = float(cost_str) if cost_str else 0.0
        if cost < 0:
            cost = 0.0
    except ValueError:
        cost = 0.0

    if service_date and description:
        maintenance.add_maintenance_log(
            device_id, session["user_id"], service_date, description, cost
        )

    return redirect(f"/devices/{device_id}")


@app.route("/admin/users")
def admin_users():
    """Render admin user overview table."""
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    all_users = users.get_all_users()
    return render_template("admin_users.html", users=all_users)


@app.route("/admin/users/<int:user_id>/privileges", methods=["POST"])
def update_user_privileges(user_id):
    """Update privilege flags for a specific user account."""
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    can_add = 1 if request.form.get("can_add") else 0
    can_edit = 1 if request.form.get("can_edit") else 0
    can_delete = 1 if request.form.get("can_delete") else 0
    users.update_user_privileges(user_id, can_add, can_edit, can_delete)
    return redirect("/admin/users")


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete a user account as administrator (preventing self-deletion)."""
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    if user_id == session["user_id"]:
        return redirect("/admin/users")
    users.delete_user(user_id)
    return redirect("/admin/users")


@app.route("/users/<int:user_id>")
def user_profile(user_id):
    """Render user profile page with activity statistics and assigned devices."""
    user = users.get_user_by_id(user_id)
    if not user:
        abort(404)
    user_devices = users.get_devices_by_user(user_id)
    stats = users.get_user_statistics(user_id)
    return render_template(
        "user_profile.html", user=user, user_devices=user_devices, stats=stats
    )


if __name__ == "__main__":
    app.run(debug=True)
