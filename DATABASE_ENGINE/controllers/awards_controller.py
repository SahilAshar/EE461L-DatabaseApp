import requests

# import mongoengine as me
# from mongoengine import *

from .database_controller import db

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


class AwardWinner(db.Document):
    name = db.StringField()
    movie = db.StringField()
    song = db.StringField()
    year = db.StringField()


class FullAward(db.Document):
    query_title = db.StringField()
    title = db.StringField()
    winners = db.ListField(db.ReferenceField(AwardWinner))


class AwardController:
    def post(self):

        self.__build_best_picture_award()
        self.__build_best_actor_award()
        self.__build_best_actress_award()
        self.__build_best_director_award()
        self.__build_best_supporting_actor_award()

    def get(self, query_award):
        matching_full_awards = FullAward.objects(
            query_title__icontains=query_award
        ).get()

        return matching_full_awards

    def get_paginated_full_awards(self, page):
        paginated_awards = FullAward.objects().paginate(page=page, per_page=9)

        return paginated_awards

    # ! Temp function for instance population
    def get_all_award_winners(self):
        all_award_objects = AwardWinner.objects()

        return all_award_objects

    def __get_best_picture_info(self):

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

    def __get_best_supporting_actor_info(self):

        best_supp_actor_json = requests.get(
            "https://api.wolframalpha.com/v2/query?"
            + "input=best+supporting+actor"
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

        best_supp_actor_str = best_supp_actor_json["queryresult"]["pods"][0]["subpods"][
            0
        ]["plaintext"]

        return best_supp_actor_str

    def __build_best_picture_award(self):
        title = "best-picture"

        info_str = self.__get_best_picture_info()
        info_list = self.__get_award_winner_list(info_str)

        self.__build_full_award(info_list, title)

    def __build_best_actor_award(self):
        title = "actor-in-a-leading-role"

        info_str = self.__get_best_actor_info()
        info_list = self.__get_award_winner_list(info_str)

        self.__build_full_award(info_list, title)

    def __build_best_actress_award(self):
        title = "actress-in-a-leading-role"

        info_str = self.__get_best_actress_info()
        info_list = self.__get_award_winner_list(info_str)

        self.__build_full_award(info_list, title)

    def __build_best_director_award(self):
        title = "directing"

        info_str = self.__get_best_director_info()
        info_list = self.__get_award_winner_list(info_str)

        self.__build_full_award(info_list, title)

    def __build_best_supporting_actor_award(self):
        title = "actor-in-a-supporting-role"

        info_str = self.__get_best_supporting_actor_info()
        info_list = self.__get_award_winner_list(info_str)

        self.__build_full_award(info_list, title)

    def __get_award_winner_list(self, award_info_str):

        award_winner_list = list(award_info_str.split("\n"))
        award_winner_list.remove(award_winner_list[0])
        award_winner_list.remove(award_winner_list[len(award_winner_list) - 1])

        return award_winner_list

    def __build_full_award(self, award_winner_list, title):
        winners = []

        for award_winner_str in award_winner_list:
            award_winner = self.__build_award_winner(award_winner_str, title)
            winners.append(award_winner)

        # Move from &&&&-&&&&-&&&& -> &&&& &&&& &&&&
        formatted_title = title.replace("-", " ")

        new_full_award = FullAward(
            query_title=title, title=formatted_title, winners=winners
        )
        new_full_award.save()

    def __build_award_winner(self, award_winner_str, title):
        # example input : '2020 | Joaquin Phoenix in Joker'

        year = ""
        movie = ""
        song = ""
        name = ""

        award_winner_list = []

        award_winner_list = list(award_winner_str.split(" | "))
        year = award_winner_list[0]

        award_winner_str = award_winner_list[1]

        if title == "best picture":

            award_winner_list = award_winner_str.split(" (")

            movie = award_winner_list[0]
            name = award_winner_list[1].replace(")", "")

        elif (
            title == "achievement in music written for motion pictures (original song)"
            or title == "music (original song)"
        ):

            award_winner_list = award_winner_str.split(" for ")
            name = award_winner_list[0]

            song_info_list = award_winner_list[1].split(" in ")

            song = song_info_list[0]
            movie = song_info_list[1]

        elif title == "foreign language film":

            movie = award_winner_str

        else:

            award_winner_list = award_winner_str.split(" in ")

            if len(award_winner_list) < 2:
                award_winner_list = award_winner_str.split(" for ")
            if len(award_winner_list) < 2:
                name = award_winner_list[0]
            else:
                name = award_winner_list[0]
                movie = award_winner_list[1]

        new_award_winner = AwardWinner(name=name, movie=movie, song=song, year=year)
        new_award_winner.save()

        return new_award_winner


if __name__ == "__main__":
    pass
