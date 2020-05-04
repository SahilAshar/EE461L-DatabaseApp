from controllers.database_controller import db


# each award nominated for or won - says winner/nominee in title
class Nomination(db.Document):
    award_title = db.StringField()
    names = db.ListField(db.StringField())


# query name is just name + " movie" to make sure api returns the movie and not just definition of word
class Movie(db.Document):
    query_title = db.StringField()
    link_title = db.StringField()
    title = db.StringField()
    director = db.StringField()
    year = db.StringField()
    gross = db.StringField()
    image_link = db.StringField()
    nominations = db.ListField(db.ReferenceField(Nomination))

    meta = {
        "indexes": [
            {
                "fields": ["$title", "$director"],
                "default_language": "english",
                "weights": {"title": 10, "director": 3},
            }
        ]
    }
