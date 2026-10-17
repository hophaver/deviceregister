import os
from flask import Flask, render_template, request, redirect, session, abort
import db
import users
import devices
import classifications

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

    user_id = session.get("user_id")
    privileges = users.get_user_privileges(user_id) if user_id else None
    can_add = bool(privileges and privileges["can_add"])

    return render_template("index.html", devices=all_devices, query=query, can_add=can_add)



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

    privileges = users.get_user_privileges(session["user_id"])
    if not privileges or not privileges["can_add"]:
        abort(403)

    all_users = users.get_all_users()
    all_classifications = classifications.get_all_classifications()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        model = request.form.get("model", "").strip() or None
        serial_number = request.form.get("serial_number", "").strip() or None
        description = request.form.get("description", "").strip() or None
        owner_id_str = request.form.get("owner_id", "").strip()
        owner_id = int(owner_id_str) if owner_id_str else None

        type_id_str = request.form.get("type_id", "").strip()
        type_id = int(type_id_str) if type_id_str else None
        category_id_str = request.form.get("category_id", "").strip()
        category_id = int(category_id_str) if category_id_str else None
        location_id_str = request.form.get("location_id", "").strip()
        location_id = int(location_id_str) if location_id_str else None
        os_id_str = request.form.get("os_id", "").strip()
        os_id = int(os_id_str) if os_id_str else None

        is_valid, error = devices.validate_device(name, model, serial_number, description)
        if not is_valid:
            return render_template(
                "new_device.html",
                users=all_users,
                classifications=all_classifications,
                error=error,
            )

        creator_id = session["user_id"]
        devices.create_device(
            name, model, serial_number, description, creator_id, owner_id,
            type_id=type_id, category_id=category_id, location_id=location_id, os_id=os_id,
        )
        return redirect("/")

    return render_template("new_device.html", users=all_users, classifications=all_classifications)


@app.route("/devices/<int:device_id>")
def device_details(device_id):
    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session.get("user_id")
    privileges = users.get_user_privileges(user_id) if user_id else None
    is_owner_or_creator = bool(user_id and (user_id == device["creator_id"] or user_id == device["owner_id"]))
    can_edit = bool(privileges and (privileges["is_admin"] or (is_owner_or_creator and privileges["can_edit"])))
    can_delete = bool(privileges and (privileges["is_admin"] or (is_owner_or_creator and privileges["can_delete"])))

    return render_template("device.html", device=device, can_edit=can_edit, can_delete=can_delete)


@app.route("/devices/<int:device_id>/edit", methods=["GET", "POST"])
def edit_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    privileges = users.get_user_privileges(user_id)
    if not privileges:
        abort(403)

    is_owner_or_creator = user_id == device["creator_id"] or user_id == device["owner_id"]
    if not privileges["is_admin"] and not (is_owner_or_creator and privileges["can_edit"]):
        abort(403)

    all_users = users.get_all_users()
    all_classifications = classifications.get_all_classifications()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        model = request.form.get("model", "").strip() or None
        serial_number = request.form.get("serial_number", "").strip() or None
        description = request.form.get("description", "").strip() or None
        owner_id_str = request.form.get("owner_id", "").strip()
        owner_id = int(owner_id_str) if owner_id_str else None

        type_id_str = request.form.get("type_id", "").strip()
        type_id = int(type_id_str) if type_id_str else None
        category_id_str = request.form.get("category_id", "").strip()
        category_id = int(category_id_str) if category_id_str else None
        location_id_str = request.form.get("location_id", "").strip()
        location_id = int(location_id_str) if location_id_str else None
        os_id_str = request.form.get("os_id", "").strip()
        os_id = int(os_id_str) if os_id_str else None

        is_valid, error = devices.validate_device(name, model, serial_number, description)
        if not is_valid:
            return render_template(
                "edit_device.html",
                device=device,
                users=all_users,
                classifications=all_classifications,
                error=error,
            )

        devices.update_device(
            device_id, name, model, serial_number, description, owner_id,
            type_id=type_id, category_id=category_id, location_id=location_id, os_id=os_id,
        )
        return redirect(f"/devices/{device_id}")

    return render_template("edit_device.html", device=device, users=all_users, classifications=all_classifications)



@app.route("/devices/<int:device_id>/delete", methods=["POST"])
def delete_device(device_id):
    if "user_id" not in session:
        return redirect("/login")

    device = devices.get_device_by_id(device_id)
    if not device:
        abort(404)

    user_id = session["user_id"]
    privileges = users.get_user_privileges(user_id)
    if not privileges:
        abort(403)

    is_owner_or_creator = user_id == device["creator_id"] or user_id == device["owner_id"]
    if not privileges["is_admin"] and not (is_owner_or_creator and privileges["can_delete"]):
        abort(403)

    devices.delete_device(device_id)
    return redirect("/")


@app.route("/admin/users")
def admin_users():
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    all_users = users.get_all_users()
    return render_template("admin_users.html", users=all_users)


@app.route("/admin/users/<int:user_id>/privileges", methods=["POST"])
def update_user_privileges(user_id):
    if "user_id" not in session or not session.get("is_admin"):
        abort(403)
    can_add = 1 if request.form.get("can_add") else 0
    can_edit = 1 if request.form.get("can_edit") else 0
    can_delete = 1 if request.form.get("can_delete") else 0
    users.update_user_privileges(user_id, can_add, can_edit, can_delete)
    return redirect("/admin/users")


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

