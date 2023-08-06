from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///wld"
db = SQLAlchemy(app)

@app.route("/")
def index():
    movs = ["DL","Squat"]
    return render_template("index.html", movs = movs)

@app.route("/profile")
def profile():
    try:
        res = db.session.execute(text('SELECT * FROM results'))
        results =  res.fetchall()
    except:
        results = ['Could not read the database']

    return render_template("profile.html", results = results)
