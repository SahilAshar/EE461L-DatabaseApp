import logging
import os
from urllib.error import HTTPError

import requests
import wikipedia

from .database_controller import db, upload_blob

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""

LOGGER = logging.getLogger(__name__)


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


class PeopleAccessController:
    # POST Request (Update Request)
    # Update the database
    def post(self, name):
        # Make it a queryable string for the WolframAlpha API
        query_name = name.replace("-", "+")

        # Return a string, delimited by \n, that gives actor name and DOB
        actor_data_str = self.__get_actor_data_str(query_name)

        wkpage = self.__set_wiki_page(query_name)

        # Return a link to an actor's image
        actor_image_link = self.__get_image_link_str(wkpage)

        wiki_image_name = self.__get_wiki_image_name(actor_image_link)

        actor_wikimedia_link = self.__get_and_store_image(query_name, actor_image_link)

        # Return a dict with actor name and DOB, parsed from actor_data_str
        actor_data_dict = self.__build_actor_data_dict(actor_data_str, query_name)

        # Create initial person document, don't save until full document is built
        actor = Person(
            query_name=query_name,
            name=actor_data_dict["full name"],
            dob=actor_data_dict["date of birth"],
            image_link=actor_wikimedia_link,
        )

        # Assign bio to actor through API call
        actor.bio = self.__get_actor_bio_str(query_name)

        # Save before implementing adding awards portion
        actor.save()

        # Return a string, delimited by \n, that gives all awards won by an actor
        actor_awards_str = self.__get_actor_awards_str(query_name)

        # Return a list of strings that describe the awards won by an actor
        actor_awards_list = self.__build_actor_awards_list(actor_awards_str)

        # Return a list of Award documents
        awards_list = self.__build_awards_list(actor_awards_list)

        # Append list of Award documents to Actor document
        actor.awards = awards_list

        actor.save()

        # ! USED ONLY FOR TESTING
        return actor

    def get(self, query_name):

        # Query all Person documents for names that contain our
        # query_name string. Case insensive.
        query_name = query_name.replace("-", "+")

        # You can only query one value at a time against fields, so you need
        # to query each part of the person's name and slowly narrow down options

        # for i in range(0, len(name_list)):
        #     matching_persons = Person.objects(name__icontains=name_list[i])

        matching_persons = Person.objects(query_name__icontains=query_name)

        # print(len(matching_persons))

        # for person in matching_persons:
        #     print(person.name)

        return matching_persons

    def get_paginated_people(self, page, view):

        if view == "descending":
            paginated_people = Person.objects.order_by("-name").paginate(
                page=page, per_page=9
            )
        elif view == "ascending":
            paginated_people = Person.objects.order_by("+name").paginate(
                page=page, per_page=9
            )

        return paginated_people

    def get_paginated_people_search(self, page, search):
        paginated_people = (
            Person.objects.search_text(search)
            .order_by("$text_score")
            .paginate(page=page, per_page=9)
        )

        return paginated_people

    def __get_actor_data_str(self, query_name):

        try:
            actor_data_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_name
                + "&includepodid=BasicInformation:PeopleData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=9U487H-VALXT3HLLQ"
            ).json()

            actor_data_str = actor_data_json["queryresult"]["pods"][0]["subpods"][0][
                "plaintext"
            ]

            return actor_data_str
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __build_actor_data_dict(self, data_str, query_name):
        data_dict = {}
        data_dict["full name"] = ""
        data_dict["date of birth"] = ""

        if data_str == "":
            return data_dict

        data_list = list(data_str.split("\n"))
        for data in data_list:
            data_str_list = list(data.split(" | "))
            if len(data_str_list) == 2:
                data_dict[data_str_list[0]] = data_str_list[1]
            else:
                data_dict[data_str_list[0]] = ""

        if data_dict["full name"] == "":
            data_dict["full name"] = query_name.replace("+", " ")

        return data_dict

    def __get_actor_bio_str(self, query_name):

        try:
            actor_bio_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_name
                + "&includepodid=WikipediaSummary:PeopleData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=9U487H-VALXT3HLLQ"
            ).json()

            actor_bio_str = actor_bio_json["queryresult"]["pods"][0]["subpods"][0][
                "plaintext"
            ]

            return actor_bio_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __get_actor_awards_str(self, query_name):

        try:
            actor_awards_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_name
                + "&includepodid=CrossPeopleData:AcademyAwardData"
                + "&format=plaintext"
                + "&output=JSON"
                + "&appid=9U487H-VALXT3HLLQ"
            ).json()

            # TODO: If numpods = 0, then they've won zero awards. Need to handle that case.

            actor_awards_str = actor_awards_json["queryresult"]["pods"][0]["subpods"][
                0
            ]["plaintext"]

            return actor_awards_str
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __build_actor_awards_list(self, actor_awards_str):
        try:
            actor_awards_list = list(actor_awards_str.split("\n"))
            actor_awards_list.remove(actor_awards_list[0])
            actor_awards_list.remove(actor_awards_list[len(actor_awards_list) - 1])

            return actor_awards_list
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return None

    def __build_awards_list(self, actor_awards_list):
        # List of Award documents to be returned
        award_list = []

        if actor_awards_list is None:
            return award_list

        for award_str in actor_awards_list:
            award_list.append(self.__build_award_doc(award_str))

        # print(str(award_list[0]))
        return award_list

    def __build_award_doc(self, award_str):
        # build Award document from string
        # e.x. 'achievement in directing (winner) | 2020 (age: 50 years) | Parasite'

        award_dict = {}
        award_dict["title"] = ""
        award_dict["movie"] = ""
        award_dict["year"] = ""

        try:
            award_list = list(award_str.split(" | "))
            award_dict["title"] = award_list[0]
            award_dict["movie"] = award_list[2]
            award_dict["year"] = list(award_list[1].split(" "))[0]
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

        new_award = Award(
            title=award_dict["title"],
            movie=award_dict["movie"],
            year=award_dict["year"],
        )

        new_award.save()

        return new_award

    def __set_wiki_page(self, query_name):

        try:
            name = query_name.replace("+", " ")
            result = wikipedia.search(name, results=1)
            wikipedia.set_lang("en")
            wkpage = wikipedia.WikipediaPage(title=result[0])

            return wkpage

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __get_image_link_str(self, wkpage):

        try:
            # actor_image_json = requests.get(
            #     "https://api.wolframalpha.com/v2/query?input="
            #     + query_name
            #     + "&includepodid=Image:PeopleData"
            #     + "&format=plaintext"
            #     + "&scantimeout=15.0"
            #     + "&output=JSON"
            #     + "&appid=9U487H-VALXT3HLLQ"
            # ).json()

            # actor_image_str = actor_image_json["queryresult"]["pods"][0]["subpods"][0][
            #     "imagesource"
            # ]

            # return actor_image_str

            image_info_json = requests.get(
                "https://en.wikipedia.org/w/api.php?action=query"
                + "&format=json"
                + "&formatversion=2"
                + "&prop=pageimages|pageterms"
                + "&piprop=original"
                + "&pilicense=any"
                + "&titles="
                + wkpage.title
            ).json()

            image_link_str = image_info_json["query"]["pages"][0]["original"]["source"]
            return image_link_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __get_wiki_image_name(self, image_link_str):
        try:
            return image_link_str.split("/")[-1]
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __get_and_store_image(self, query_name, image_link_str):

        try:
            print(image_link_str)
            return image_link_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""


if __name__ == "__main__":
    pa_controller = PeopleAccessController()
    people = pa_controller.get("rami-malek")
