from sqlalchemy.sql import text
from flask import session
import secrets
from werkzeug.security import check_password_hash, generate_password_hash
from .db import db


def get_users():
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
    return users_list


def get_user(user_id):
    result_user = db.session.execute(text(
            """
            SELECT users.username, users.id,
            wl.max_weight AS wl_max, wl.division AS wl_div,
            pl.max_weight AS pl_max, pl.division AS pl_div
            FROM users
            LEFT JOIN classes AS wl
            ON users.wl_class_id = wl.id
            LEFT JOIN classes as pl
            ON users.pl_class_id = pl.id
            WHERE users.id = :uid
            """), {"uid": user_id})
    lookup_user = result_user.fetchone()
    return lookup_user


def login(username, password):
    res = db.session.execute(
        text("""Select id, password, admin FROM users WHERE username =:username"""), {
            "username": username})
    user = res.fetchone()
    if not user:
        return False
    user_hash = user.password
    if check_password_hash(user_hash, password):
        session["user"] = {"username": username, "id": user.id}
        session["admin"] = user.admin
        session["csrf_token"] = secrets.token_hex(16)
        return True
    return False


def logout():
    del session["user"]
    del session["admin"]
    del session["csrf_token"]


def register(username, password, admin, wl_class, pl_class):
    pswd_hs = generate_password_hash(password)
    try:
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
        return True

    except BaseException:
        return False


def delete(user_id):
    query = text(
        """
        DELETE FROM users
        WHERE users.id = :id
        """)
    db.session.execute(query, {"id": user_id})
    db.session.commit()
