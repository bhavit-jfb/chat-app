from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.vzxgwtehuvcsdqguerfo:IRzDBYSu4wZmG5Bn@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(200), nullable=False)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    print("Login:", email)

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    groups = Group.query.all()
    return render_template("dashboard.html", groups=groups)

@app.route("/create-group", methods=["POST"])
def create_group():
    group_name = request.form.get("group_name")

    new_group = Group(
        id=str(uuid.uuid4()),
        name=group_name
    )

    db.session.add(new_group)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/send-message", methods=["POST"])
def send_message():
    message = request.form.get("message")
    file = request.files.get("file")

    print("Message:", message)

    if file:
        print("File name:", file.filename)

    return jsonify({"status": "Message received"})

@app.route("/group/<group_id>")
def group_chat(group_id):
    group = Group.query.get(group_id)
    return render_template("group_chat.html", group=group)

if __name__ == "__main__":
    app.run(debug=True)