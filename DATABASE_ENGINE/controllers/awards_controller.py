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

    def __get_best_picture_info(self):
        title = "Best Picture"

        best_picture_json = requests.get(
            "https://api.wolframalpha.com/v2/query?"
            + "input=best+picture"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&includepodid=Result"
            + "&format=plaintext"
            + "&output=JSON"
            # adding the timeout in the GET request allows us to
            # ignore having to use the recalculation link.
            # Latency in building isn't important to us, accuracy is.
            + "&scantimeout=15.0"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        best_picture_str = best_picture_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return best_picture_str

    def __get_best_actor_info(self):
        title = "Actor in a Leading Role"

        best_actor_json = requests.get(
            "https://api.wolframalpha.com/v2/query?"
            + "input=best+actor"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&includepodid=Result"
            + "&format=plaintext"
            + "&output=JSON"
            # adding the timeout in the GET request allows us to
            # ignore having to use the recalculation link.
            # Latency in building isn't important to us, accuracy is.
            + "&scantimeout=15.0"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        best_actor_str = best_actor_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return best_actor_str

    def __get_best_actress_info(self):
        title = "Actress in a Leading Role"

        best_actress_json = requests.get(
            "https://api.wolframalpha.com/v2/query?"
            + "input=best+actress"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&includepodid=Result"
            + "&format=plaintext"
            + "&output=JSON"
            # adding the timeout in the GET request allows us to
            # ignore having to use the recalculation link.
            # Latency in building isn't important to us, accuracy is.
            + "&scantimeout=15.0"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        best_actress_str = best_actress_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return best_actress_str

    def __get_best_director_info(self):
        title = "Directing"

        best_director_json = requests.get(
            "https://api.wolframalpha.com/v2/query?"
            + "input=best+director"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&includepodid=Result"
            + "&format=plaintext"
            + "&output=JSON"
            # adding the timeout in the GET request allows us to
            # ignore having to use the recalculation link.
            # Latency in building isn't important to us, accuracy is.
            + "&scantimeout=15.0"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        best_director_str = best_director_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return best_director_str


if __name__ == "__main__":
    pass
