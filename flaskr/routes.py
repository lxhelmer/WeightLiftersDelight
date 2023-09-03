from flask import render_template, request, redirect, session, abort
from sqlalchemy.sql import text
from .app import app
from .db import db
from . import result_service
from . import user_service
from . import sport_service
from .privileges import not_login, is_admin
from .orders import orders

#Order of route file
#Visible sites
#User management
#Result management
#Competition management

#Home page
@app.route("/", methods=["GET"])
@app.route("/<message>")
def index(message=""):
    if not_login():
        return redirect("/landing")
    admin = is_admin()

    error = ""
    notif = ""

    if message == "fail":
        error = "Failed to add new entry!"
    elif message =="cfail":
        error = "Failed to add new competition!"
    elif message == "ok":
        notif = "Added new entry!"
    elif message =="cadd":
        notif = "Added new competition!"

    entrys = sport_service.get_lifts()
    comps = sport_service.get_competitions()        
    publics = result_service.get_public()

    return render_template(
        "index.html", entrys=entrys, notif=notif, error=error,
        publics=publics, sports=["WL", "PL"],
        admin=admin, comps=comps)


#Visible site for non log-in usage.
@app.route("/landing")
def landing():
    return render_template("landing.html")

#Site for creating new user.
@app.route("/register")
@app.route("/register/<error>")
def register(error=""):
    #This is to avoid the possibility of rendering user input in html
    if error == "name":
        error = "Select another name"
    elif error == "fields":
        error = "Please fill all fields"
    elif error == "match":
        error = "Passwords do not match"
    else:
        error = ""

    return render_template("register.html", error=error)

#Profile-page for normal users, wraps /user/id implementation.
@app.route("/profile", methods=["GET"])
def profile():
    if not_login():
        return redirect("/landing")
    return user_page(session["user"]["id"])


#Per result page.
@app.route("/result/<int:res_id>", methods= ["GET"])
def result_page(res_id):
    if not_login():
        return redirect("/landing")

    username = session["user"]["username"]

    lift_info, comments = result_service.get_result(res_id)
    if lift_info == None:
        return redirect("/")

    if lift_info.username == username or lift_info.public:
        return render_template(
            "result.html",
            info=lift_info,
            comments=comments,
        )
    return redirect("/profile")


#Admin view of all the users.
@app.route("/users")
def users():
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)

    users_list = user_service.get_users()
    return render_template("users.html", users=users_list)

#Per user view (wrapped by /profile).
@app.route("/user/<int:usr_id>", methods=["GET"])
def user_page(usr_id):
    if not_login():
        return redirect("/landing")
    
    user = session["user"]

    results = result_service.get_results(user_id=usr_id)
    #Get the user being viewed
    viewed = user_service.get_user(usr_id)

    #Value for determining how the page should be displayed
    profile = (usr_id == user["id"])

    if is_admin():
        return render_template("user.html", results=results, user=user,
                               orders=orders.values(), profile=profile,
                               viewed=viewed)
    
    return render_template("user.html", results=results, user=user,
                           orders=orders.values(),
                           profile=True, viewed=user)

#User management:
#Add new user
@app.route("/newu", methods=["POST"])
def new_user():

    username = request.form["nusername"]
    pswd_tx = request.form["password"]
    pswd_tx_snd = request.form["password_snd"]
    admin = request.form["admin"]
    wl = request.form["weightlifting"]
    pl = request.form["powerlifting"]
    division = request.form["division"]
    weight = request.form["weight"]

    wl_class = None
    pl_class = None

    print(pswd_tx)
    print(pswd_tx_snd)
    print(pswd_tx == pswd_tx_snd)
    if pswd_tx != pswd_tx_snd:
        return redirect("/register/match")

    if weight == "" or username == "" or pswd_tx == "":
        return redirect("/register/fields")

    #Checking against string 0 is not elegant but
    #it makes it possible to always fetch the form value
    if wl == "0" and pl == "0":
        return redirect("/register/fields")

    if wl != "0":
        wl_class = sport_service.get_class("WL", division, weight)

    if pl != "0":
        pl_class = sport_service.get_class("PL", division, weight)

    if user_service.register(username, pswd_tx, admin, wl_class, pl_class, division, weight):
        return redirect("/")
    return redirect("/register/name")

#Remove user
@app.route("/removeu/<u_id>", methods=["GET"])
def removeu(u_id):
    if not_login():
        return redirect("/landing")
    if is_admin():
        user_service.delete(u_id)
        return redirect("/users")
    return redirect("/")

#User login.
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    pswd_tx = request.form["password"]

    if user_service.login(username,pswd_tx):
        return redirect("/")
    return redirect("/landing")

#User logout
@app.route("/logout")
def logout():
    if not_login():
        return redirect("/landing")
    user_service.logout()
    return redirect("/")


#Result management:
#Add new result
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

    result_service.add_result(user,lift, weight, public, comp)
    return redirect("/ok") 

#Remove result
@app.route("/remove/<res_id>", methods=["GET"])
def remove(res_id):
    if not_login():
        return redirect("/landing")
    route = result_servie.delete_resutl(res_id)
    return redirect(route)

#Like a result
@app.route("/like/<res_id>", methods=["GET"])
def like(res_id):
    result_service.like_result(res_id)
    return redirect("/result/" + res_id)

#Set result filter
@app.route("/setselected/<u_id>", methods=["POST"])
def setSelected(u_id):
    session["selected"] = request.form["lift"]
    print(request.form["lift"])
    if is_admin():
        return redirect("/user/"+str(u_id))
    return redirect("/profile")

#Set result order
@app.route("/setorder/<u_id>", methods=["POST"])
def setOrder(u_id):
    session["order"] = request.form["order"]
    if is_admin():
        return redirect("/user/"+str(u_id))
    return redirect("/profile")

#Add new competition
@app.route("/sendcomp", methods=["POST"])
def send_comp():
    if not_login():
        return redirect("/landing")
    if not is_admin():
        abort(403)
    sport = request.form["sport"]
    name = request.form["name"]
    if name == "":
        return redirect("/cfail")

    sport_service.add_competition(name,sport)
    return redirect("/cadd")

