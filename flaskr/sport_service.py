from .db import db

def get_lifts():
    result = db.session.execute(text(
        """
            select lift from movements
        """))
    lifts = result.fetchall()
    return lifts

get_competitions():
    comp_query = text("""
                      SELECT name, id, sport FROM competitions
                      """)
    comp_result = db.session.execute(comp_query)
    competitions = comp_result.fetchall()
    return competitions
