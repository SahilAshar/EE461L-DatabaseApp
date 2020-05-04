from controllers.database_controller import db


class Award(db.Document):
    title = db.StringField()
    winner = db.StringField()
    movie = db.StringField()
    year = db.StringField()


class Person(db.Document):
    query_name = db.StringField(required=True)
    name = db.StringField()
    dob = db.StringField()
    bio = db.StringField()
    occupation = db.StringField()
    years_active = db.StringField()
    image_link = db.StringField()
    awards = db.ListField(db.ReferenceField(Award))

    meta = {
        "indexes": [
            {
                "fields": ["$name", "$bio"],
                "default_language": "english",
                "weights": {"name": 10, "bio": 2},
            }
        ]
    }
