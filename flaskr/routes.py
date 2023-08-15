from datetime import datetime
from .app import app
from flask import render_template, request, redirect, session, abort
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from .db import db

def not_login():
    return session.get("username") is None

@app.route("/")
@app.route("/<message>")
def index(message=""):
    # This is not the most elegant way of
    # doing the check and redirect but it works now.
    # Might change to flask_login later.
    if not_login():
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


@app.route("/profile", methods=["GET","POST"])
def profile(selected="%"):
    if not_login():
        abort(403)

    user = session["username"]
    user_id = db.session.execute(
        text("""SELECT id FROM users WHERE username=:u"""), {"u": user})
    uid = user_id.fetchone().id

    res = db.session.execute(text(
        """
        SELECT results.id,results.weight,results.date,movements.lift FROM results
        LEFT JOIN movements ON results.movement_id = movements.id
        WHERE results.user_id =:u AND movements.lift LIKE :s ORDER BY results.date DESC
        """), {"u": uid, "s": selected})
    results = res.fetchall()

    
    return render_template("profile.html", results=results)


@app.route("/filter", methods=["POST"])
def filter_results():
    if not_login():
        return redirect("/landing")
    selected = request.form["lift"]
    if selected == "Clear":
        return redirect("/profile")
    return profile(selected)


@app.route("/sendres", methods=["POST"])
def send_result():
    if not_login():
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
        (user_id, movement_id, weight, date, public) values (:a,:b,:c,:d,:p)""")
    db.session.execute(query, {"a": uid, "b": lift_t, "c": weight, "d": date, "p":True})
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
    if not_login():
        return redirect("/landing")

    del session["username"]
    return redirect("/")


@app.route("/register")
def register():

    return render_template("register.html")


@app.route("/newu", methods=["POST"])
def new_user():

    username = request.form["nusername"]
    pswd_tx = request.form["password"]
    pswd_hs = generate_password_hash(pswd_tx)
    query = text(
        """INSERT INTO users (username, password, admin) VALUES (:u, :p, :a)"""
        )
    db.session.execute(query, {"u": username, "p": pswd_hs, "a": False})
    db.session.commit()
    return redirect("/")


@app.route("/landing")
def landing():
    return render_template("landing.html")

@app.route("/remove/<id>", methods=["POST"])
def remove(id):
    if not_login():
        return redirect("/landing")
    user = session["username"]
    query = text(
            """
                 DELETE FROM results
                 WHERE results.id IN 
                 (SELECT results.id 
                  FROM results LEFT JOIN users 
                  ON results.user_id = users.id
                  WHERE results.id =:id AND users.username=:user)
            """)
    db.session.execute(query, {"id":id, "user":user})
    db.session.commit()
    return redirect("/profile")
    
    
@app.route("/result/<id>", methods=["POST"])
def result_page(id):
    if not_login():
        return redirect("/landing")

    user = session["username"]

    query = text("""
                 SELECT results.id, users.username, results.public, results.weight,
                 movements.lift, results.date, classes.sport, classes.open,
                 classes.max_weight, results.like_amount
                 FROM results
                 LEFT JOIN movements
                 ON results.movement_id= movements.id
                 LEFT JOIN users
                 ON results.user_id = users.id
                 LEFT JOIN classes
                 ON results.class_id = classes.id
                 """)
    result = db.session.execute(query, {"id":id})
    lift_info = result.fetchone()

    print(user)
    print(lift_info.username)
    print(lift_info.public)
    if lift_info.username == user or lift_info.public:
        query = text("""
                     SELECT comment
                     FROM comments
                     WHERE result_id =:lift_id
                     """)
        result = db.session.execute(query, {"lift_id":lift_info.id})
        comments = result.fetchall()

        return render_template(
                "result.html",
                info = lift_info,
                comments = comments,
                )
    return redirect("/profile")

    
    
