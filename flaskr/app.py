from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from datetime import datetime


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///wld"
db = SQLAlchemy(app)

@app.route("/")
def index():
    res = db.session.execute(text(
        '''
            select lift from movements
        '''))
    movs = res.fetchall()
    return render_template("index.html", movs = movs)

@app.route("/profile")
def profile():
    try:
        res = db.session.execute(text(
        '''
            SELECT results.weight,results.date,movements.lift FROM results 
            LEFT JOIN movements on results.movement_id = movements.id
            '''))
        results =  res.fetchall()
    except:
        results = ['Could not read the database']

    return render_template("profile.html", results = results)

@app.route("/send", methods=["POST"])
def send():
    lift = request.form['lift']
    wg = request.form['weight']
    date = datetime.today().strftime('%Y-%m-%d')

    #I don't like this way of getting the lift id but it handles the changes and new lifts quite well
    #might try to get rid of it later
    res = db.session.execute(
            text('''SELECT id FROM movements WHERE lift=:x'''),{'x':lift})

    lift_t = res.fetchall()[0][0]

    query = text('INSERT INTO results (user_id, movement_id, weight, date) values (:a,:b,:c,:d)')
    db.session.execute(query, {'a':1,'b':lift_t,'c':int(wg),'d':date})
    db.session.commit()
    return redirect("/")


