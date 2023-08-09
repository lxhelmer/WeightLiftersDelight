from datetime import datetime
from os import getenv
from flask import Flask
from flask import render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)


def check_login():
    return session.get("username") is None

@app.route("/")
@app.route("/<message>")
def index(message=""):
    # This is not the most elegant way of
    # doing the check and redirect but it works now.
    # Might change to flask_login later.
    if check_login():
        return redirect("/landing")

    error = ""
    notif = ""

    if message == "fail":
        error = "Failed to add new entry. :("
    elif message == "ok":
        notif = "Added new entry!"
    else:
        notif = ""

    res = db.session.execute(text(
        """
            select lift from movements
        """))
    entrys = res.fetchall()
    return render_template("index.html", entrys=entrys, notif=notif, error=error)


@app.route("/profile")
def profile(selected="%"):
    if check_login():
        return redirect("/landing")

    user = session["username"]
    user_id = db.session.execute(
        text("""SELECT id FROM users WHERE username=:u"""), {"u": user})
    uid = user_id.fetchone().id
    print(uid)

    res = db.session.execute(text(
        """
        SELECT results.weight,results.date,movements.lift FROM results
        LEFT JOIN movements on results.movement_id = movements.id
        WHERE results.user_id =:u AND movements.lift LIKE :s ORDER BY results.date DESC
        """), {"u": uid, "s": selected})
    results = res.fetchall()

    return render_template("profile.html", results=results)


@app.route("/filter", methods=["POST"])
def filter_results():
    if check_login():
        return redirect("/landing")
    selected = request.form["lift"]
    if selected == "Clear":
        return redirect("/profile")
    return profile(selected)


@app.route("/sendres", methods=["POST"])
def send_result():
    if check_login():
        return redirect("/landing")

    user = session["username"]
    lift = request.form["lift"]
    weight = request.form["weight"]
    try:
        weight = float(weight)
    except ValueError:
        return redirect("/fail")
    date = datetime.today().strftime("%Y-%m-%d")

    # I don"t like this way of getting the lift
    # id but it handles the changes and new lifts quite well
    # might try to get rid of it later
    lift_type = db.session.execute(
        text("""SELECT id FROM movements WHERE lift=:x"""), {"x": lift})
    lift_t = lift_type.fetchone().id

    user_id = db.session.execute(
        text("""SELECT id FROM users WHERE username=:u"""), {"u": user})
    uid = user_id.fetchone().id

    query = text(
        """INSERT INTO results
        (user_id, movement_id, weight, date) values (:a,:b,:c,:d)""")
    db.session.execute(query, {"a": uid, "b": lift_t, "c": weight, "d": date})
    db.session.commit()
    return redirect("/ok")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    pswd_tx = request.form["password"]
    res = db.session.execute(
        text("""Select id, password FROM users WHERE username =:username"""), {
            "username": username})
    user = res.fetchone()
    if not user:
        return redirect("/")
    user_hash = user.password
    if check_password_hash(user_hash, pswd_tx):
        session["username"] = username
        return redirect("/")
    return redirect("/landing")


@app.route("/logout")
def logout():
    if check_login():
        return redirect("/landing")
    del session["username"]
    return redirect("/")


@app.route("/register")
def register():
    if check_login():
        return redirect("/landing")

    return render_template("register.html")


@app.route("/newu", methods=["POST"])
def new_user():
    if check_login():
        return redirect("/landing")

    username = request.form["nusername"]
    pswd_tx = request.form["password"]
    pswd_hs = generate_password_hash(pswd_tx)
    query = text(
        "INSERT INTO users (username, password, admin) VALUES (:u, :p, :a)")
    db.session.execute(query, {"u": username, "p": pswd_hs, "a": False})
    db.session.commit()
    return redirect("/")


@app.route("/landing")
def landing():
    return render_template("landing.html")
