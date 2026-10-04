import os
from flask import Flask, render_template, request, redirect, session
import db
import users

app = Flask(__name__)
app.secret_key = os.urandom(24)
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


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


if __name__ == "__main__":
    app.run(debug=True)

