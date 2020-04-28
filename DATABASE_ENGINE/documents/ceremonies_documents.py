from controllers.database_controller import db


class Nominee(db.Document):
    song = db.StringField()
    name = db.StringField()
    movie = db.StringField()


class YearAward(db.Document):
    title = db.StringField()
    nominees = db.ListField(db.ReferenceField(Nominee))


class Year(db.Document):
    ceremony_name = db.StringField()
    query_ceremony = db.StringField()
    movies_year = db.StringField()
    hosted_year = db.StringField()
    host = db.StringField()
    site = db.StringField()
    ceremony_summary = db.StringField()
    image_link = db.StringField()
    awards = db.ListField(db.ReferenceField(YearAward))

    meta = {
        "indexes": [
            {
                "fields": [
                    "$ceremony_name",
                    "$movies_year",
                    "$hosted_year",
                    "$ceremony_summary",
                ],
                "default_language": "english",
                "weights": {
                    "ceremony_name": 10,
                    "movies_year": 2,
                    "hosted_year": 2,
                    "ceremony_summary": 5,
                },
            }
        ]
    }
