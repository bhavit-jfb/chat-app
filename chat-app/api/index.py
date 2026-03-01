import os
from flask import Flask
# from extensions import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db.init_app(app)

@app.route("/")
def home():
    return "Flask working on Vercel 🚀"

app = app
