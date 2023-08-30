from flask import render_template, request, redirect, session, abort
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from .app import app
from .db import db
from . import results
from .privileges import not_login, is_admin



@app.route("/", methods=["GET", "POST"])
@app.route("/<message>")
def index(message=""):
    # This is not the most elegant way of
    # doing the check and redirect but it works now.
    # Might change to flask_login later.
    if not_login():
        return redirect("/landing")
    admin = is_admin()

    error = ""
    notif = ""

    if message == "fail":
        error = "Failed to add new entry."
    elif message == "ok":
        notif = "Added new entry!"
    else:
        notif = ""

    lifts = db.session.execute(text(
        """
            select lift from movements
        """))
    entrys = lifts.fetchall()

    res_query = text(
        """
        SELECT results.id,results.weight,results.date,
        movements.lift, users.username, users.admin
        FROM results
        LEFT JOIN movements
        ON results.movement_id = movements.id
        LEFT JOIN users
        ON results.user_id = users.id
        WHERE results.public ORDER BY results.date DESC
        """)
    public_results = db.session.execute(res_query)
    publics = public_results.fetchall()

    comp_query = text("""
                      SELECT name, id, sport FROM competitions
                      """)
    comp_result = db.session.execute(comp_query)
    competitions = comp_result.fetchall()

    return render_template(
        "index.html", entrys=entrys, notif=notif, error=error,
        publics=publics, sports=["WL", "PL"],
        admin=admin, comps=competitions)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not_login():
        return redirect("/landing")
    return user_page(session["user"]["id"])
    
@app.route("/setselected", methods=["POST"])
def setSelected():
    session["selected"] = request.form["lift"]
    print(request.form["lift"])
    return redirect("/profile")

@app.route("/setorder", methods=["POST"])
def setOrder():
    session["order"] = request.form["order"]
    return redirect("/profile")


@app.route("/sendres", methods=["POST"])
def send_result():
    if not_login():
        return redirect("/landing")

    user = session["user"]
    lift = request.form["lift"]
    weight = request.form["weight"]
    public = request.form["public"]
    comp = request.form["comp"]

    try:
        weight = float(weight)
    except ValueError:
        return redirect("/fail")

    results.add_result(user,lift, weight, public, comp)

    return redirect("/ok")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    pswd_tx = request.form["password"]
    res = db.session.execute(
        text("""Select id, password, admin FROM users WHERE username =:username"""), {
            "username": username})
    user = res.fetchone()
    if not user:
        return redirect("/")
    user_hash = user.password
    if check_password_hash(user_hash, pswd_tx):
        session["user"] = {"username":username,"id":user.id}
        session["admin"] = user.admin

        return redirect("/")
    return redirect("/landing")


@app.route("/logout")
def logout():
    if not_login():
        return redirect("/landing")

    del session["user"]
    del session["admin"]
    return redirect("/")


@app.route("/register")
def register():

    return render_template("register.html")


@app.route("/newu", methods=["POST"])
def new_user():

    username = request.form["nusername"]
    pswd_tx = request.form["password"]
    admin = request.form["admin"]
    weightlifting = request.form["weightlifting"]
    powerlifting = request.form["powerlifting"]
    division = request.form["division"]
    weight = request.form["weight"]

    wl_class = None
    pl_class = None

    if weightlifting:
        wl_query = text("""
                           SELECT id
                           FROM classes WHERE sport = 'WL' AND division =:d AND max_weight > :w
                           ORDER by max_weight ASC
                           """)
        result = db.session.execute(wl_query, {"d": division, "w": weight})
        wl_class = result.fetchone().id

    if powerlifting:
        pl_query = text("""
                           SELECT id
                           FROM classes WHERE sport = 'PL' AND division =:d AND max_weight > :w
                           ORDER by max_weight ASC
                           """)
        result = db.session.execute(pl_query, {"d": division, "w": weight})
        pl_class = result.fetchone().id

    pswd_hs = generate_password_hash(pswd_tx)
    query = text(
        """INSERT INTO users 
        (username, password, admin, wl_class_id, pl_class_id)
        VALUES (:u, :p, :a, :wl, :pl)"""
    )
    db.session.execute(query, {"u": username,
                               "p": pswd_hs,
                               "a": admin,
                               "wl": wl_class,
                               "pl": pl_class})
    db.session.commit()
    return redirect("/")


@app.route("/landing")
def landing():
    return render_template("landing.html")


@app.route("/remove/<res_id>", methods=["POST"])
def remove(res_id):
    if not_login():
        return redirect("/landing")
    if is_admin():
        query = text(
            """
                     DELETE FROM results
                     WHERE results.id IN
                     (SELECT results.id
                      FROM results LEFT JOIN users
                      ON results.user_id = users.id
                      WHERE results.id =:id)
                     RETURNING results.user_id
                """)
        result = db.session.execute(query, {"id": res_id, })
        user_id = result.fetchone().user_id
        db.session.commit()
        return redirect("/user/" + str(user_id))

    user = session["user"]["username"]
    query = text(
        """
                 DELETE FROM results
                 WHERE results.id IN
                 (SELECT results.id
                  FROM results LEFT JOIN users
                  ON results.user_id = users.id
                  WHERE results.id =:id AND users.username=:user)
            """)
    db.session.execute(query, {"id": id, "user": user})
    db.session.commit()
    return redirect("/profile")


@app.route("/result/<res_id>", methods=["POST", "GET"])
def result_page(res_id):
    if not_login():
        return redirect("/landing")

    user = session["user"]["username"]

    query = text("""
                 SELECT results.id, users.username, results.public, results.weight,
                 movements.lift, results.date,
                 results.like_amount
                 FROM results
                 LEFT JOIN movements
                 ON results.movement_id= movements.id
                 LEFT JOIN users
                 ON results.user_id = users.id
                 WHERE results.id = :id
                 """)
    result = db.session.execute(query, {"id": res_id})
    lift_info = result.fetchone()

    if lift_info.username == user or lift_info.public:
        query = text("""
                     SELECT comment
                     FROM comments
                     WHERE result_id =:lift_id
                     """)
        result = db.session.execute(query, {"lift_id": lift_info.id})
        comments = result.fetchall()

        return render_template(
            "result.html",
            info=lift_info,
            comments=comments,
        )
    return redirect("/profile")


@app.route("/users")
def users():
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)
    query = text("""
                 SELECT users.id, users.username,
                 wl.max_weight AS wl_max, wl.division AS wl_div,
                 pl.max_weight AS pl_max, pl.division AS pl_div
                 FROM users
                 LEFT JOIN classes AS wl
                 ON users.wl_class_id = wl.id
                 LEFT JOIN classes as pl
                 ON users.pl_class_id = pl.id
                 """)
    result = db.session.execute(query)
    users_list = result.fetchall()

    return render_template("users.html", users=users_list)


@app.route("/user/<usr_id>", methods=["POST", "GET"])
def user_page(usr_id):
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)
    
    selected = "%"
    order = "dnf"

    if session.get("selected"):
        selected = session["selected"]

    if session.get("order"):
        order = session["order"]

    orders = {
        "whf": ("weight high first", "whf", "results.weight DESC"),
        "wlf": ("weight low first", "wlf", "results.weight ASC"),
        "dnf": ("date new first", "dnf", "results.date DESC"),
        "dof": ("date old first", "dof", "results.date ASC")
    }

    order = orders[order][2]

    result = db.session.execute(text(
        """
        SELECT results.id,results.weight,results.date,
        movements.lift, results.user_id, users.username
        FROM results
        LEFT JOIN movements ON results.movement_id = movements.id
        LEFT JOIN users ON results.user_id = users.id
        WHERE results.user_id =:u AND movements.lift LIKE :s
        """), {"u": usr_id, "s": selected})
    results = result.fetchall()

    user = session["user"]

    return render_template("user.html", results=results, user=user, orders=orders.values())


@app.route("/sendcomp", methods=["POST"])
def send_comp():
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)
    sport = request.form["sport"]
    name = request.form["name"]

    comp_query = text("""
                      INSERT INTO competitions (name, sport) VALUES (:n, :s)
                      """)
    db.session.execute(comp_query, {"n": name, "s": sport})
    db.session.commit()
    return redirect("/")


@app.route("/like/<res_id>", methods=["POST"])
def like(res_id):
    like_query = text("""
                      UPDATE results
                      SET like_amount = like_amount + 1
                      WHERE id = :id
                      """)
    db.session.execute(like_query,{"id":res_id})
    db.session.commit()
    return redirect("/result/" + res_id)


@app.route("/removeu/<u_id>", methods=["POST"])
def removeu(u_id):
    if not_login():
        return redirect("/landing")
    if is_admin():
        query = text(
            """
                     DELETE FROM users
                     WHERE users.id = :id

                """)
        result = db.session.execute(query, {"id": u_id})
        db.session.commit()
        return redirect("/users")
    return redirect("/")













