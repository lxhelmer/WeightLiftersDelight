from sqlalchemy.sql import text
from datetime import datetime
from .db import db

def add_result(user, lift, weight, public, comp):

    date = datetime.today().strftime("%Y-%m-%d")

    if comp == "":
        comp = None

    # I don"t like this way of getting the lift
    # id but it handles the changes and new lifts well

    lift_type = db.session.execute(
        text("""SELECT id FROM movements WHERE lift=:x"""), {"x": lift})
    lift_t = lift_type.fetchone().id

    user_id = user["id"]

    query = text(
        """INSERT INTO results
        (user_id, movement_id, weight, date, public, comp_id) values (:a,:b,:c,:d,:p, :cid)""")
    db.session.execute(query,
                       {"a": user_id,
                        "b": lift_t,
                        "c": weight,
                        "d": date,
                        "p": public,
                        "cid": comp})
    db.session.commit()

