from datetime import datetime
from sqlalchemy.sql import text
from flask import session
from .db import db
from .orders import orders
from .privileges import is_admin


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


def get_public():
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

    return publics


def get_results(user_id):
    selected = "%"
    order = "dnf"

    if session.get("selected"):
        selected = session["selected"]

    if session.get("order"):
        order = session["order"]

    order = orders[order][2]

    # If the current user is not admin
    # it always gets its own results.
    if not is_admin():
        user_id = session["user"]["id"]

    result = db.session.execute(text(
        """
        SELECT results.id,results.weight,results.date,
        movements.lift, results.user_id, users.username
        FROM results
        LEFT JOIN movements ON results.movement_id = movements.id
        LEFT JOIN users ON results.user_id = users.id
        WHERE results.user_id =:u AND movements.lift LIKE :s ORDER BY
        """ + order), {"u": user_id, "s": selected})
    results = result.fetchall()
    return results


def get_result(result_id):
    query = text("""
                 SELECT results.id, users.username, results.public, results.weight,
                 movements.lift, results.date,
                 results.like_amount, competitions.name AS comp_name
                 FROM results
                 LEFT JOIN movements
                 ON results.movement_id = movements.id
                 LEFT JOIN users
                 ON results.user_id = users.id
                 LEFT JOIN competitions
                 ON results.comp_id = competitions.id
                 WHERE results.id = :id
                 """)
    result = db.session.execute(query, {"id": result_id})
    lift_info = result.fetchone()
    return (lift_info, get_comments(result_id))


def like_result(result_id):
    like_query = text("""
                      UPDATE results
                      SET like_amount = like_amount + 1
                      WHERE id = :id
                      """)
    db.session.execute(like_query, {"id": result_id})
    db.session.commit()


def delete_result(result_id):
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
        result = db.session.execute(query, {"id": result_id, })
        user_id = result.fetchone().user_id
        db.session.commit()
        return "/user/" + str(user_id)

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
    return "/profile"


def add_comment(result_id, comment):
    query = text(
        """
            INSERT INTO comments
            (comment, result_id) values (:c, :id)
            """)
    db.session.execute(query, {"c": comment, "id": result_id})
    db.session.commit()


def get_comments(result_id):
    query = text("""
             SELECT comment
             FROM comments
             WHERE comments.result_id =:lift_id
             """)
    result = db.session.execute(query, {"lift_id": result_id})
    comments = result.fetchall()
    return comments
