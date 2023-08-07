from flask import Flask
from flask import render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

@app.route("/")
def index():
    if not session:
        return redirect("/profile")

    res = db.session.execute(text(
        '''
            select lift from movements
        '''))
    movs = res.fetchall()
    return render_template("index.html", movs = movs)

@app.route("/profile")
def profile():
    user = session['username']
    user_id = db.session.execute(
            text('''SELECT id FROM users WHERE username=:u'''), {'u':user})
    uid = user_id.fetchone().id
    try:
        res = db.session.execute(text(
        '''
            SELECT results.weight,results.date,movements.lift FROM results 
            LEFT JOIN movements on results.movement_id = movements.id
            WHERE results.id =:u
            '''),{'u':uid})
        results =  res.fetchall()
    except:
        results = ['Could not read the database']

    return render_template("profile.html", results = results)

@app.route("/sendres", methods=["POST"])
def send():
    user = session['username']
    lift = request.form['lift']
    wg = request.form['weight']
    date = datetime.today().strftime('%Y-%m-%d')

    #I don't like this way of getting the lift id but it handles the changes and new lifts quite well
    #might try to get rid of it later
    lift_type = db.session.execute(
            text('''SELECT id FROM movements WHERE lift=:x'''),{'x':lift})
    lift_t = lift_type.fetchone().id

    user_id = db.session.execute(
            text('''SELECT id FROM users WHERE username=:u'''), {'u':user})
    uid = user_id.fetchone().id

    query = text('INSERT INTO results (user_id, movement_id, weight, date) values (:a,:b,:c,:d)')
    db.session.execute(query, {'a':uid,'b':lift_t,'c':int(wg),'d':date})
    db.session.commit()
    return redirect("/")

@app.route("/login", methods=["POST"])
def login():
    username = request.form['username']
    pswd_tx = request.form['password']
    res = db.session.execute(text('''Select id, password FROM users WHERE username =:username'''), {'username':username})
    user = res.fetchone()
    if not user:
        return redirect("/")
    else:
        user_hash = user.password
        if check_password_hash(user_hash,pswd_tx):
            session['username'] = username
            return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/register")
def register():
    return render_template("register.html")
    
@app.route("/newu", methods=["POST"])
def newu():
    username = request.form['nusername']
    pswd_tx = request.form['password']
    pswd_hs = generate_password_hash(pswd_tx)
    query = text("INSERT INTO users (username, password, admin) VALUES (:u, :p, :a)")
    db.session.execute(query, {'u':username, 'p':pswd_hs, 'a':False})
    db.session.commit()
    return redirect("/")




    
