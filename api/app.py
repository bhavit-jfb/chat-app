from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies
)
from flask import make_response
import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_COOKIE_SECURE"] = True  # True in production with HTTPS
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    created_by = db.Column(db.String, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GroupMember(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    group_id = db.Column(db.String, db.ForeignKey("groups.id"))
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = db.Column(db.String, db.ForeignKey("groups.id"))
    user_id = db.Column(db.String, db.ForeignKey("users.id"))
    content = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)
        new_user = User(
            id=str(uuid.uuid4()),
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return "Invalid credentials", 401

    access_token = create_access_token(identity=user.id)

    response = make_response(redirect("/dashboard"))
    set_access_cookies(response, access_token)

    return response

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

@app.route("/create-message", methods=["POST"])
@jwt_required()
def create_message():
    current_user_id = get_jwt_identity()

    content = request.form.get("content")

    new_message = Message(
        id=str(uuid.uuid4()),
        content=content,
        user_id=current_user_id
    )

    db.session.add(new_message)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/logout")
def logout():
    response = make_response(redirect("/"))
    unset_jwt_cookies(response)
    return response

# ❌ REMOVE app.run() completely
