import requests

from .database_controller import db


"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


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
    awards = db.ListField(db.ReferenceField(Award))


class PeopleAccessController:
    # POST Request (Update Request)
    # Update the database
    def post(self, name):
        # Make it a queryable string for the WolframAlpha API
        query_name = name.replace("-", "+")

        # Return a string, delimited by \n, that gives actor name and DOB
        actor_data_str = self.__get_actor_data_str(query_name)

        # Return a dict with actor name and DOB, parsed from actor_data_str
        actor_data_dict = self.__build_actor_data_dict(actor_data_str, query_name)

        # Create initial person document, don't save until full document is built
        actor = Person(
            query_name=query_name,
            name=actor_data_dict["full name"],
            dob=actor_data_dict["date of birth"],
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

        #for testing
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

    def get_paginated_people(self, page):
        paginated_people = Person.objects.paginate(page=page, per_page=9)

        return paginated_people

    def __get_actor_data_str(self, query_name):

        actor_data_json = requests.get(
            "https://api.wolframalpha.com/v2/query?input="
            + query_name
            + "&includepodid=BasicInformation:PeopleData"
            + "&format=plaintext"
            + "&output=JSON"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        actor_data_str = actor_data_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return actor_data_str

    def __build_actor_data_dict(self, data_str, query_name):
        data_dict = {}
        data_dict["full name"] = ""
        data_dict["date of birth"] = ""

        data_list = list(data_str.split("\n"))
        for data in data_list:
            # print(data)
            data_str_list = list(data.split(" | "))
            if len(data_str_list) == 2:
                data_dict[data_str_list[0]] = data_str_list[1]
            else:
                data_dict[data_str_list[0]] = ""

        if data_dict["full name"] == "":
            data_dict["full name"] = query_name.replace("+", " ")

        return data_dict

    def __get_actor_bio_str(self, query_name):
        actor_bio_json = requests.get(
            "https://api.wolframalpha.com/v2/query?input="
            + query_name
            + "&includepodid=WikipediaSummary:PeopleData"
            + "&format=plaintext"
            + "&output=JSON"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        actor_bio_str = actor_bio_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return actor_bio_str

    def __get_actor_awards_str(self, query_name):
        actor_awards_json = requests.get(
            "https://api.wolframalpha.com/v2/query?input="
            + query_name
            + "&includepodid=CrossPeopleData:AcademyAwardData"
            + "&format=plaintext"
            + "&output=JSON"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        # TODO: If numpods = 0, then they've won zero awards. Need to handle that case.

        actor_awards_str = actor_awards_json["queryresult"]["pods"][0]["subpods"][0][
            "plaintext"
        ]

        return actor_awards_str

    def __build_actor_awards_list(self, actor_awards_str):
        actor_awards_list = list(actor_awards_str.split("\n"))
        actor_awards_list.remove(actor_awards_list[0])
        actor_awards_list.remove(actor_awards_list[len(actor_awards_list) - 1])

        return actor_awards_list

    def __build_awards_list(self, actor_awards_list):
        # List of Award documents to be returned
        award_list = []

        for award_str in actor_awards_list:
            award_list.append(self.__build_award_doc(award_str))

        print(str(award_list[0]))
        return award_list


    def __build_award_doc(self, award_str):
        # build Award document from string
        # e.x. 'achievement in directing (winner) | 2020 (age: 50 years) | Parasite'

        award_dict = {}
        award_dict["title"] = ""
        award_dict["movie"] = ""
        award_dict["year"] = ""

        award_list = list(award_str.split(" | "))
        award_dict["title"] = award_list[0]
        award_dict["movie"] = award_list[2]
        award_dict["year"] = list(award_list[1].split(" "))[0]

        new_award = Award(
            title=award_dict["title"],
            movie=award_dict["movie"],
            year=award_dict["year"],
        )

        new_award.save()

        return new_award


if __name__ == "__main__":
    pa_controller = PeopleAccessController()
    people = pa_controller.get("rami-malek")
