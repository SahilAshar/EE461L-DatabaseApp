import requests

# import mongoengine as me
# from mongoengine import *

from .database_controller import db

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


class Award(db.Document):
    title = db.StringField()
    movie = db.StringField()
    year = db.StringField()


class AwardController:
    def post(self):
        return None

    def get(self):
        return None

