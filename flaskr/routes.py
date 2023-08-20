from datetime import datetime
from .app import app
from flask import render_template, request, redirect, session, abort
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash
from .db import db

def not_login():
    return session.get("username") is None

def is_admin():
    return session.get("admin")
        
@app.route("/", methods=["GET","POST"])
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
    
    query = text(
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
    public_results = db.session.execute(query)
    publics = public_results.fetchall()

    return render_template(
            "index.html", entrys=entrys, notif=notif, error=error,
            publics=publics, sports=["WL","PL"], admin=admin)


@app.route("/profile", methods=["GET","POST"])
@app.route("/profile/<filter>", methods=["GET","POST"])
def profile(filter="%"):
    if not_login():
        return redirect("/landing")

    user = session["username"]
    user_id = db.session.execute(
        text("""SELECT id FROM users WHERE username=:u"""), {"u": user})
    uid = user_id.fetchone().id

    res = db.session.execute(text(
        """
        SELECT results.id,results.weight,results.date,movements.lift FROM results
        LEFT JOIN movements ON results.movement_id = movements.id
        WHERE results.user_id =:u AND movements.lift LIKE :f ORDER BY results.date DESC
        """), {"u": uid, "f": filter})
    results = res.fetchall()

    return render_template("profile.html", results=results)



@app.route("/sendres", methods=["POST"])
def send_result():
    if not_login():
        return redirect("/landing")

    user = session["username"]
    lift = request.form["lift"]
    weight = request.form["weight"]
    public = request.form["public"]
    print(public)
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
    db.session.execute(query, {"a": uid, "b": lift_t, "c": weight, "d": date, "p":public})
    db.session.commit()
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
        session["username"] = username
        session["admin"] = user.admin

        return redirect("/")
    return redirect("/landing")


@app.route("/logout")
def logout():
    if not_login():
        return redirect("/landing")

    del session["username"]
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
        wl_query= text("""
                           SELECT id
                           FROM classes WHERE sport = 'WL' AND division =:d AND max_weight > :w
                           ORDER by max_weight ASC
                           """)
        result = db.session.execute(wl_query, {"d":division,"w":weight})
        wl_class = result.fetchone().id


    if powerlifting:
        pl_query = text("""
                           SELECT id
                           FROM classes WHERE sport = 'PL' AND division =:d AND max_weight > :w
                           ORDER by max_weight ASC
                           """)
        result = db.session.execute(pl_query, {"d":division,"w":weight})
        pl_class = result.fetchone().id

    pswd_hs = generate_password_hash(pswd_tx)
    query = text(
        """INSERT INTO users (username, password, admin, wl_class_id, pl_class_id) VALUES (:u, :p, :a, :wl, :pl)"""
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

@app.route("/remove/<id>", methods=["POST"])
def remove(id):
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
        result = db.session.execute(query, {"id":id,})
        user_id = result.fetchone().user_id
        db.session.commit()
        return redirect("/user/" + str(user_id))

        
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
                 movements.lift, results.date, classes.sport, classes.division,
                 classes.max_weight, results.like_amount
                 FROM results
                 LEFT JOIN movements
                 ON results.movement_id= movements.id
                 LEFT JOIN users
                 ON results.user_id = users.id
                 LEFT JOIN classes
                 ON users.class_id = classes.id
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

    
    
@app.route("/users")
def users():
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)
    query = text("""
                 SELECT users.id, users.username, 
                 wl.max_weight AS wl_max, wl.division AS wl_div,
                 pl.max_weight AS pl_max, pl.division AS PL_div
                 FROM users
                 LEFT JOIN classes AS wl
                 ON users.wl_class_id = wl.id
                 LEFT JOIN classes as PL
                 ON users.pl_class_id = wl.id
                 """)
    result = db.session.execute(query)
    users = result.fetchall()

    

    return render_template("users.html", users=users)

@app.route("/user/<id>/<selected>", methods=["POST", "GET"])
@app.route("/user/<id>", methods=["POST", "GET"])
def user(id, selected="%"):
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)

    result = db.session.execute(text(
        """
        SELECT results.id,results.weight,results.date,
        movements.lift, results.user_id, users.username
        FROM results
        LEFT JOIN movements ON results.movement_id = movements.id
        LEFT JOIN users ON results.user_id = users.id
        WHERE results.user_id =:u AND movements.lift LIKE :s ORDER BY results.date DESC
        """), {"u": id, "s": selected})
    results = result.fetchall()

    #There is no nice way of getting the name when there is
    #no results for that users
    user_result = db.session.execute(
            text("""SELECT users.username, users.id FROM users WHERE users.id =:id"""),
            {"id": id}
            )
    user = user_result.fetchone()
    

    return render_template("user.html", results=results, user=user)
