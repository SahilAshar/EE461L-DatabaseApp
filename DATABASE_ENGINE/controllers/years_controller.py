import logging
import os
from urllib.error import HTTPError

import requests
import wikipedia
import wptools

from .database_controller import db, upload_blob

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""

LOGGER = logging.getLogger(__name__)
WOLFRAM_API_KEY = "RQV64G-3A2ALKAP6A"


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


class YearController:

    # GET Request only for years
    # No need for POST, no updating done
    # Initial POST used for building DB

    # TODO: Make POST uneccesary by abstracting Award logic elsewhere
    def post(self, ceremony_name, year):

        hosted_year = str(int(year) + 1)
        movies_year = str(year)

        # Return a string, delimited by \n, that gives actor name and DOB
        all_year_awards_str = self.__get_all_year_awards_str(hosted_year)

        # Return a list of all award strings from the all_year_awards_str
        all_year_awards_str_list = self.__get_all_year_awards_str_list(
            all_year_awards_str
        )

        # Return a list of all built Award documents, built from a list of award strings
        year_award_list = self.__build_year_awards_list(all_year_awards_str_list)

        ceremony_name = ceremony_name

        query_ceremony = ceremony_name.lower().replace(" ", "+")

        wkpage = self.__set_wiki_page(ceremony_name)

        host, site = self.__get_host_and_site(wkpage)

        host, site = self.__parse_host_and_site(host, site)

        ceremony_summary_str = self.__get_ceremony_summary_str(wkpage)
        image_link_str = self.__get_image_link_str(wkpage)

        wiki_image_name = self.__get_wiki_image_name(image_link_str)
        wiki_image_link = self.__get_and_store_image(
            query_ceremony, wiki_image_name, image_link_str
        )

        year = Year(
            ceremony_name=ceremony_name,
            query_ceremony=query_ceremony,
            movies_year=movies_year,
            hosted_year=hosted_year,
            host=host,
            site=site,
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

    def get_ceremony_name_by_year(self, query_year):

        query_year = str(int(query_year) + 1)

        matching_years = Year.objects(hosted_year__iexact=query_year).get()
        return matching_years.query_ceremony

    def get_paginated_years(self, page, view):

        if view == "descending":
            paginated_years = Year.objects.order_by("-hosted_year").paginate(
                page=page, per_page=9
            )
        elif view == "ascending":
            paginated_years = Year.objects.order_by("+hosted_year").paginate(
                page=page, per_page=9
            )

        return paginated_years

    def get_paginated_years_search(self, page, search):

        paginated_years = (
            Year.objects.search_text(search)
            .order_by("$text_score")
            .paginate(page=page, per_page=9)
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
            + "&appid="
            + WOLFRAM_API_KEY
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

    def __get_host_and_site(self, wkpage):

        host = "n/a"
        site = ""

        try:
            awards_page = wptools.page(wkpage.title).get_parse()
            infobox = awards_page.data["infobox"]
            site = infobox["site"]
            host = infobox["host"]
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

        return host, site

    def __get_ceremony_summary_str(self, wkpage):

        return wkpage.summary

    def __get_image_link_str(self, wkpage):

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

        try:
            print(image_link_str)
            return image_link_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

        # print(wiki_image_name)

        # try:
        #     if wiki_image_name == "":
        #         raise KeyError

        #     file_name = wiki_image_name

        #     print(file_name)

        #     r = requests.get(image_link_str, allow_redirects=True)
        #     open("./temp/years/" + file_name, "wb").write(r.content)

        #     file_name = file_name.replace(".JPG", ".jpg")

        #     upload_blob(
        #         "ceremony-images-databaseengine",
        #         "./temp/years/" + file_name + "",
        #         query_ceremony,
        #     )

        #     return (
        #         "https://storage.googleapis.com/ceremony-images-databaseengine/"
        #         + query_ceremony
        #     )

        # except Exception as e:
        #     message = f"Error: {e}"
        #     LOGGER.exception(message)
        #     return ""

    def __parse_host_and_site(self, host, site):
        host = self.__parse_host(host)
        site = self.__parse_site(site)
        return host, site

    def __parse_host(self, host):
        host = host.replace("and <br />", "and ").replace(", <br />", ", ").replace("<br />", ", ")
        host = host.replace("<br> ", ", ").replace(" and <br>", ", ").replace("<br>", ", ")

        if "{" in host:
            host = host[:host.index("{")]

        final_hosts = []
        host_split = host.split("[[")
        for person in host_split:
            if "|" in person:
                person = person.split("|")
                person = person[1].replace("]]", "")
            else:
                person = person.replace("]]", "")
            final_hosts.append(person)

        return "".join(final_hosts)

    def __parse_site(self, site):
        if "{" in site:
            if "ref" in site:
                site = site[:site.index("{")] + site[site.index("}") + 3:]
            else:
                site = site.split("|")[1:]
                site = ", ".join(site)

        site = site.replace(" <br />", ", ").replace(",<br />", ", ").replace(" <br /> ", ", ").replace("<br />", ", ")
        site = site.replace("<br/>", ", ")
        site = site.replace(", <br>", ", ").replace("and <br>", ", ").replace(" <br>", ", ").replace("<br>", ", ")

        final_site = []
        site_split = site.split("[[")
        for place in site_split:
            if "|" in place:
                place = place.split("|")
                place = place[1].replace("]]", "")
            else:
                place = place.replace("]]", "")
            final_site.append(place)

        return "".join(final_site)


if __name__ == "__main__":
    y_controller = YearController()
    y_controller.post(1995)
    # year = y_controller.get(1995)
