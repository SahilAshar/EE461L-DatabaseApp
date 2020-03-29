import requests
from .database_controller import db


"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


class Nominee(db.Document):
    song = db.StringField()
    name = db.StringField()
    movie = db.StringField()


class YearAward(db.Document):
    title = db.StringField()
    nominees = db.ListField(db.ReferenceField(Nominee))


class Year(db.Document):
    year = db.StringField()
    awards = db.ListField(db.ReferenceField(YearAward))


class YearController:

    # GET Request only for years
    # No need for POST, no updating done
    # Initial POST used for building DB

    # TODO: Make POST uneccesary by abstracting Award logic elsewhere
    def post(self, year):

        year_num = str(year)

        # Return a string, delimited by \n, that gives actor name and DOB
        all_year_awards_str = self.__get_all_year_awards_str(year_num)

        # Return a list of all award strings from the all_year_awards_str
        all_year_awards_str_list = self.__get_all_year_awards_str_list(
            all_year_awards_str
        )

        # Return a list of all built Award documents, built from a list of award strings
        year_award_list = self.__build_year_awards_list(all_year_awards_str_list)

        year = Year(year=year, awards=year_award_list)

        year.save()

        return year

    # TODO: Change all of this to be DB query of all Award objects
    # Query by year instead, and get all awards associated with that year
    def get(self, query_year):

        matching_years = Year.objects(year__icontains=query_year).get()

        return matching_years

    def get_paginated_years(self, page):
        paginated_years = Year.objects.order_by("year").paginate(page=page, per_page=9)

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
            + "&scantimeout=15.0"
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

        year_award_info_list = list(year_award_str.split(" | "))
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


if __name__ == "__main__":
    y_controller = YearController()
    y_controller.post(1995)
    # year = y_controller.get(1995)
