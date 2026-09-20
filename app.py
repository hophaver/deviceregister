import os
from flask import Flask, render_template
import db

app = Flask(__name__)
app.secret_key = os.urandom(24)
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
