from flask import session


def not_login():
    return session.get("user") is None


def is_admin():
    return session.get("admin")
