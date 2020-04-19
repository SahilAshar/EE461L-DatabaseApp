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
    year = db.StringField()
    ceremony_summary = db.StringField()
    image_link = db.StringField()
    awards = db.ListField(db.ReferenceField(YearAward))


class YearController:

    # GET Request only for years
    # No need for POST, no updating done
    # Initial POST used for building DB

    # TODO: Make POST uneccesary by abstracting Award logic elsewhere
    def post(self, ceremony_name, year):

        year_num = str(year)

        # Return a string, delimited by \n, that gives actor name and DOB
        all_year_awards_str = self.__get_all_year_awards_str(year_num)

        # Return a list of all award strings from the all_year_awards_str
        all_year_awards_str_list = self.__get_all_year_awards_str_list(
            all_year_awards_str
        )

        # Return a list of all built Award documents, built from a list of award strings
        year_award_list = self.__build_year_awards_list(all_year_awards_str_list)

        ceremony_name = ceremony_name

        query_ceremony = ceremony_name.lower().replace(" ", "+")

        wkpage = self.__set_wiki_page(ceremony_name)

        ceremony_summary_str = self.__get_ceremony_summary_str(wkpage)
        image_link_str = self.__get_image_link_str(wkpage)

        wiki_image_name = self.__get_wiki_image_name(image_link_str)
        wiki_image_link = self.__get_and_store_image(
            query_ceremony, wiki_image_name, image_link_str
        )

        year = Year(
            ceremony_name=ceremony_name,
            query_ceremony=query_ceremony,
            year=year,
            ceremony_summary=ceremony_summary_str,
            image_link=wiki_image_link,
            awards=year_award_list,
        )

        year.save()

        return year

    # TODO: Change all of this to be DB query of all Award objects
    # Query by year instead, and get all awards associated with that year
    def get(self, query_ceremony):

        matching_years = Year.objects(query_ceremony__iexact=query_ceremony).get()

        return matching_years

    def get_paginated_years(self, page, view):

        if view == "descending":
            paginated_years = Year.objects.order_by("-year").paginate(
                page=page, per_page=9
            )
        elif view == "ascending":
            paginated_years = Year.objects.order_by("year").paginate(
                page=page, per_page=9
            )

        return paginated_years

    # Makes initial API call and returns a str of all awards
    # associated with a specific year
    def __get_all_year_awards_str(self, year_num):

        all_year_awards_json = requests.get(
            "https://api.wolframalpha.com/v2/query?input="
            + "Academy+award+"
            + year_num
            + "&podstate=Result__More"
            + "&podstate=Result__More"
            + "&includepodid=Result"
            + "&format=plaintext"
            + "&output=JSON"
            + "&scantimeout=30.0"
            + "&appid=9U487H-VALXT3HLLQ"
        ).json()

        all_year_awards_str = all_year_awards_json["queryresult"]["pods"][0]["subpods"][
            0
        ]["plaintext"]

        return all_year_awards_str

    def __get_all_year_awards_str_list(self, all_year_awards_str):

        all_year_awards_str_list = list(all_year_awards_str.split("\n"))

        return all_year_awards_str_list

    def __build_year_awards_list(self, all_year_awards_str_list):

        # List of Year Award documents to be built and returned
        year_award_list = []

        for year_award_str in all_year_awards_str_list:
            year_award_list.append(self.__build_year_award_doc(year_award_str))

        return year_award_list

    def __build_year_award_doc(self, year_award_str):
        try:
            year_award_info_list = list(year_award_str.split(" | "))
            print(year_award_info_list)

            title = year_award_info_list[0]
            nominee_info_str = year_award_info_list[1]

            # TODO: handle nominee builder for multiple nominees
            nominees_list = []
            nominees_list.append(self.__build_nominee_doc(nominee_info_str, title))

            new_year_award = YearAward(
                title=year_award_info_list[0], nominees=nominees_list
            )

            new_year_award.save()

            return new_year_award
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __build_nominee_doc(self, nominee_info_str, title):

        song = ""
        name = ""
        movie = ""

        if title == "best motion picture" or title == "best picture":

            nominee_info_list = nominee_info_str.split(" (")

            movie = nominee_info_list[0]
            name = nominee_info_list[1].replace(")", "")

        elif (
            title == "achievement in music written for motion pictures (original song)"
            or title == "music (original song)"
        ):

            nominee_info_list = nominee_info_str.split(" for ")
            name = nominee_info_list[0]

            song_info_list = nominee_info_list[1].split(" in ")

            song = song_info_list[0]
            movie = song_info_list[1]

        elif title == "foreign language film":

            movie = nominee_info_str

        else:

            nominee_info_list = nominee_info_str.split(" in ")

            if len(nominee_info_list) < 2:
                nominee_info_list = nominee_info_str.split(" for ")
            if len(nominee_info_list) < 2:
                name = nominee_info_list[0]
            else:
                name = nominee_info_list[0]
                movie = nominee_info_list[1]

        new_nominee = Nominee(song=song, name=name, movie=movie)
        new_nominee.save()

        return new_nominee

    def __set_wiki_page(self, ceremony_name):
        result = wikipedia.search(ceremony_name, results=1)
        wikipedia.set_lang("en")
        wkpage = wikipedia.WikipediaPage(title=result[0])

        return wkpage

    def __get_ceremony_summary_str(self, wkpage):

        return wkpage.summary

    def __build_ceremony_summary(self, ceremony_summary_str):
        return None

    def __get_image_link_str(self, wkpage):

        # ordinal_num = wkpage.title.split(" ")[0]

        # for image in wkpage.images:
        #     if ordinal_num in image:
        #         return image

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

        try:
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

    def __get_and_store_image(self, query_ceremony, wiki_image_name, image_link_str):
        print(wiki_image_name)

        try:
            if wiki_image_name == "":
                raise KeyError

            file_name = wiki_image_name

            print(file_name)

            # os.system(
            #     "download_from_Wikimedia_Commons "
            #     + "'"
            #     + file_name
            #     + "'"
            #     + " --output ./temp/years/ --width 300"
            # )

            r = requests.get(image_link_str, allow_redirects=True)
            open("./temp/years/" + file_name, "wb").write(r.content)

            file_name = file_name.replace(".JPG", ".jpg")

            upload_blob(
                "ceremony-images-databaseengine",
                "./temp/years/" + file_name + "",
                query_ceremony,
            )

            return (
                "https://storage.googleapis.com/ceremony-images-databaseengine/"
                + query_ceremony
            )

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""


if __name__ == "__main__":
    y_controller = YearController()
    y_controller.post(1995)
    # year = y_controller.get(1995)
