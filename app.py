import os
from flask import Flask, render_template, request, redirect, session, abort
import db
import users
import devices

app = Flask(__name__)
app.secret_key = os.urandom(24)
db.init_app(app)


@app.route("/")
def index():
    query = request.args.get("query", "").strip()
    if query:
        all_devices = devices.search_devices(query)
    else:
        all_devices = devices.get_all_devices()
    return render_template("index.html", devices=all_devices, query=query)


@app.route("/register", methods=["GET", "POST"])
def register():
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
    session.clear()
    return redirect("/")


@app.route("/devices/new", methods=["GET", "POST"])
def new_device():
    if "user_id" not in session:
        return redirect("/login")

    all_users = users.get_all_users()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        model = request.form.get("model", "").strip() or None
        serial_number = request.form.get("serial_number", "").strip() or None
        description = request.form.get("description", "").strip() or None
        owner_id_str = request.form.get("owner_id", "").strip()
        owner_id = int(owner_id_str) if owner_id_str else None

        is_valid, error = devices.validate_device(name, model, serial_number, description)
        if not is_valid:
            return render_template("new_device.html", users=all_users, error=error)

        creator_id = session["user_id"]
        devices.create_device(name, model, serial_number, description, creator_id, owner_id)
        return redirect("/")

    return render_template("new_device.html", users=all_users)


@app.route("/devices/<int:device_id>")
def device_details(device_id):
    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)
    return render_template("device.html", device=device)


@app.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
def edit_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    is_admin = session.get("is_admin", False)

    if not is_admin and user_id != device["creator_id"] and user_id != device["owner_id"]:
        abort(403)

    all_users = users.get_all_users()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        model = request.form.get("model", "").strip() or None
        serial_number = request.form.get("serial_number", "").strip() or None
        description = request.form.get("description", "").strip() or None
        owner_id_str = request.form.get("owner_id", "").strip()
        owner_id = int(owner_id_str) if owner_id_str else None

        is_valid, error = devices.validate_device(name, model, serial_number, description)
        if not is_valid:
            return render_template(
                "edit_device.html",
                device=device,
                users=all_users,
                error=error,
            )

        devices.update_device(device_id, name, model, serial_number, description, owner_id)
        return redirect(f"/devices/{device_id}")

    return render_template("edit_device.html", device=device, users=all_users)


@app.route("/devices/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    is_admin = session.get("is_admin", False)

    if not is_admin and user_id != device["creator_id"] and user_id != device["owner_id"]:
        abort(403)

    devices.delete_device(device_id)
    return redirect("/")


@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    all_users = users.get_all_users()
    return render_template("admin_users.html", users=all_users)


@app.route("/admin/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    if user_id == session["user_id"]:
        return redirect("/admin/users")
    users.delete_user(user_id)
    return redirect("/admin/users")


if __name__ == "__main__":
    app.run(debug=True)

