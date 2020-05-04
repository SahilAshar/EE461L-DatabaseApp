import logging

import requests
import wikipedia
import wptools

from documents.ceremonies_documents import Year, YearAward, Nominee

LOGGER = logging.getLogger(__name__)
WOLFRAM_API_KEY = "RQV64G-3A2ALKAP6A"


class CeremoniesParser:
    def parse(self, ceremony_name, year):
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
        host = self.__parse_host(host)
        site = self.__parse_site(site)

        ceremony_summary_str = self.__get_ceremony_summary_str(wkpage)
        image_link_str = self.__get_image_link_str(wkpage)

        wiki_image_link = self.__get_and_store_image(query_ceremony, image_link_str)

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

        return year

    def update_attributes_for_all_years(self):

        for year in Year.objects():

            wkpage = self.__set_wiki_page(year.ceremony_name)

            host, site = self.__get_host_and_site(wkpage)

            host = self.__parse_host(host)
            site = self.__parse_site(site)

            year.update(host=host, site=site)
            year.reload()

            try:
                print(year.host + " | " + year.site)
            except Exception as e:
                message = f"Error: {e}"
                LOGGER.exception(message)

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

    def __parse_host(self, host):
        try:
            host = host.replace("{{", "")
            host = host.replace("}}", "")
            host = host.replace("[[", "")
            host = host.replace("]]", "")
            host = host.replace("<small>", "")
            host = host.replace("</small>", "")
            host = host.replace("small", "")
            host = host.replace("|", "")
            host = host.replace("<br />", " ")
            host = host.replace("<br>", " ")
            host = host.replace("&nbsp;", " ")
            host = host.replace("{{nbsp}}", "")

            return host
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

    def __parse_site(self, site):
        try:
            site = site.replace("{{", "")
            site = site.replace("}}", "")
            site = site.replace("[[", "")
            site = site.replace("]]", "")
            site = site.replace("<small>", "")
            site = site.replace("</small>", "")
            site = site.replace("small", "")
            site = site.replace("|", " ")
            site = site.replace("<br />", " ")
            site = site.replace("<br/>", " ")
            site = site.replace("<br>", " ")
            site = site.replace("{{Sfn|Cowie|1990|p|=|132}}", "")
            site = site.replace("&nbsp;", " ")
            site = site.replace("{{nbsp}}", "")
            site = site.replace("{{sfn|Box Office Mojo staff}}", "")

            return site
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)

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

    def __get_and_store_image(self, query_ceremony, image_link_str):

        try:
            print(image_link_str)
            return image_link_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""
