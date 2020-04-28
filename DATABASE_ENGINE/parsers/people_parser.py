import logging

import requests
import wikipedia
import wptools

from documents.people_documents import Award, Person

LOGGER = logging.getLogger(__name__)
WOLFRAM_API_KEY = "RQV64G-3A2ALKAP6A"

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


class PeopleParser:
    def parse(self, name):

        # Make it a queryable string for the WolframAlpha API
        query_name = name.replace("-", "+")

        # Return a string, delimited by \n, that gives actor name and DOB
        actor_data_str = self.__get_actor_data_str(query_name)

        wkpage = self.__set_wiki_page(query_name)

        occupation = self.__get_occupation_from_infobox(wkpage)
        years_active = self.__get_years_active_from_infobox(wkpage)

        occupation = self.__parse_occupation(occupation)
        years_active = self.__parse_years_active(years_active)

        # Return a link to an actor's image
        actor_image_link = self.__get_image_link_str(wkpage)

        actor_wikimedia_link = self.__get_and_store_image(query_name, actor_image_link)

        # Return a dict with actor name and DOB, parsed from actor_data_str
        actor_data_dict = self.__build_actor_data_dict(actor_data_str, query_name)

        # Create initial person document, don't save until full document is built
        actor = Person(
            query_name=query_name,
            name=actor_data_dict["full name"],
            dob=actor_data_dict["date of birth"],
            occupation=occupation,
            years_active=years_active,
            image_link=actor_wikimedia_link,
        )

        # Assign bio to actor through API call
        actor.bio = self.__get_actor_bio_str(query_name)

        # Return a string, delimited by \n, that gives all awards won by an actor
        actor_awards_str = self.__get_actor_awards_str(query_name)

        # Return a list of strings that describe the awards won by an actor
        actor_awards_list = self.__build_actor_awards_list(actor_awards_str)

        # Return a list of Award documents
        awards_list = self.__build_awards_list(actor_awards_list)

        # Append list of Award documents to Actor document
        actor.awards = awards_list

        return actor

    def update_attributes_for_all_people(self):

        for person in Person.objects():
            query_name = person.query_name
            wkpage = self.__set_wiki_page(query_name)

            occupation = self.__get_occupation_from_infobox(wkpage)
            years_active = self.__get_years_active_from_infobox(wkpage)

            occupation = self.__parse_occupation(person.occupation)
            years_active = self.__parse_years_active(person.years_active)

            # person = Person(occupation=occupation, years_active=years_active)
            person.update(occupation=occupation, years_active=years_active)
            person.reload()

            try:
                print(person.occupation + " | " + person.years_active)
            except Exception as e:
                message = f"Error: {e}"
                LOGGER.exception(message)

    def __get_actor_data_str(self, query_name):

        try:
            actor_data_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_name
                + "&includepodid=BasicInformation:PeopleData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid="
                + WOLFRAM_API_KEY
            ).json()

            print(actor_data_json)

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

        try:
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
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
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
                + "&appid="
                + WOLFRAM_API_KEY
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
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid="
                + WOLFRAM_API_KEY
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

    def __get_occupation_from_infobox(self, wkpage):

        occupation = "n/a"

        try:
            awards_page = wptools.page(wkpage.title).get_parse()
            infobox = awards_page.data["infobox"]
            occupation = infobox["occupation"]
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

        return occupation

    def __get_years_active_from_infobox(self, wkpage):

        years_active = "n/a"

        try:
            awards_page = wptools.page(wkpage.title).get_parse()
            infobox = awards_page.data["infobox"]
            years_active = infobox["years_active"]
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

        return years_active

    def __parse_occupation(self, occupation):

        try:
            occupation = occupation.replace("{{", "")
            occupation = occupation.replace("}}", "")
            occupation = occupation.replace("[[", "")
            occupation = occupation.replace("]]", "")
            occupation = occupation.replace(
                "|<!--DO NOT REMOVE. See [[Talk:Alec Baldwin#Comedian?]] for more details.-->|",
                "",
            )
            occupation = occupation.replace("plainlist| *", "")
            occupation = occupation.replace("flatlist| * ", "")
            occupation = occupation.replace("hlist|", "")
            occupation = occupation.replace("|", ", ")
            occupation = occupation.replace("* ", ", ")
            occupation = occupation.replace(" *", ", ")
            occupation = occupation.replace("<br>", ", ")
            occupation = occupation.replace("flatlist", "")
            occupation = occupation.replace(" ,", ", ")

            return occupation
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

    def __parse_years_active(self, years_active):

        try:
            years_active = years_active.replace("&ndash;", "-")

            return years_active
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

    def __get_image_link_str(self, wkpage):

        try:
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

    def __get_and_store_image(self, query_name, image_link_str):

        try:
            print(image_link_str)
            return image_link_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""
