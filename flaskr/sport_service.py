from sqlalchemy.sql import text
from .db import db

def get_lifts():
    result = db.session.execute(text(
        """
            select lift from movements
        """))
    lifts = result.fetchall()
    return lifts

def get_competitions():
    comp_query = text("""
                      SELECT name, id, sport FROM competitions
                      """)
    comp_result = db.session.execute(comp_query)
    competitions = comp_result.fetchall()
    return competitions

def get_class(sport, division, weight):
    class_query = text("""
                    SELECT id
                    FROM classes WHERE sport = :s AND division =:d AND max_weight > :w
                    ORDER by max_weight ASC
                    """)
    result = db.session.execute(class_query, {"s":sport, "d": division, "w": weight})
    sport_class = result.fetchone().id
    return sport_class

def add_competition(name,sport):
    comp_query = text("""

                      INSERT INTO competitions (name, sport) VALUES (:n, :s)
                      """)
    db.session.execute(comp_query, {"n": name, "s": sport})
    db.session.commit()

