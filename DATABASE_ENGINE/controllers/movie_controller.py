import logging
import requests
import wikipedia

# from .database_controller import db
from DATABASE_ENGINE.controllers.database_controller import db

LOGGER = logging.getLogger(__name__)


# each award nominated for or won - says winner/nominee in title
class Nomination(db.Document):
    award_title = db.StringField()
    names = db.ListField(db.StringField())


# query name is just name + " movie" to make sure api returns the movie and not just definition of word
class Movie(db.Document):
    query_title = db.StringField()
    link_title = db.StringField()
    title = db.StringField()
    director = db.StringField()
    year = db.StringField()
    image_link = db.StringField()
    nominations = db.ListField(db.ReferenceField(Nomination))


class MovieController:
    # clear movie_checker.txt when controller made. will write during post calls
    def __init__(self):
        checker = open("movie_checker.txt", "w")
        checker.truncate(0)
        checker.close()

    def post(self, title):
        checker = open("movie_checker.txt", "a+")

        query_title = title.replace("-", "+")
        if "film" not in query_title:
            query_title += "+film"

        query_title = self.__handle_edge_cases(query_title)

        # Return string with movie title, director, and year and other info
        movie_info_str = self.__get_movie_info_str(
            query_title.replace("&", "and"), checker
        )

        # return dict with title, dir, yr from movie_info_str // dict helpful bc each index can be label from json
        movie_info_dict = self.__put_info_in_dict(movie_info_str)

        # now will get image data from wikipedia api
        wkpage_title_str = self.__find_wiki_page_title(query_title, checker)

        wiki_img_link_str = self.__get_wiki_img_link(wkpage_title_str, checker)

        link_str = movie_info_dict["title"]
        link_str = link_str.lower()
        link_str = link_str.replace(" ", "+")

        mov = Movie(
            query_title=query_title,
            link_title=link_str,
            title=movie_info_dict["title"],
            director=movie_info_dict["director"],
            year=movie_info_dict["release date"],
            image_link=wiki_img_link_str,
        )

        mov.save()

        # get string with all awards nominations
        mov_noms_str = self.__get_movie_noms_str(
            query_title.replace("&", "and"), checker
        )

        # now make string into list of nomination strings
        mov_noms_list = self.__make_nom_list(mov_noms_str)

        # turn mov_noms_list into list of nomination objects and place into movie
        mov.nominations = self.__make_nom_list_of_objs(mov_noms_list)

        mov.save()

        print(Movie.objects.count())
        checker.close()

    def get(self, query_title):
        # format title to be same as query title in post
        # query_title = title.replace("-", "+")

        # now find movies in db that have same query_title as movie you want to get
        movies_found = Movie.objects(link_title__iexact=query_title).get()

        # movies_found should only have length 1 if populated correctly so will just return 1 movie
        return movies_found

    def get_paginated_movies(self, page, view):

        if view == "descending":
            paginated_movies = Movie.objects.order_by("-title").paginate(
                page=page, per_page=9
            )
        elif view == "ascending":
            paginated_movies = Movie.objects.order_by("+title").paginate(
                page=page, per_page=9
            )

        return paginated_movies

    def __get_movie_info_str(self, query_title, checker):
        try:
            movie_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_title
                + "&includepodid=BasicInformation:MovieData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=LWUJE3-527ATY4RER"
            ).json()

            movie_json = movie_json["queryresult"]["pods"][0]["subpods"][0]["plaintext"]

            return movie_json
        except Exception as e:
            # if query title resulted in error, try query title with film attached to title
            try:
                query_title_list = query_title.split("+(")
                query_title = query_title_list[0]
                query_title += "+film"

                movie_json = requests.get(
                    "https://api.wolframalpha.com/v2/query?input="
                    + query_title
                    + "&includepodid=BasicInformation:MovieData"
                    + "&format=plaintext"
                    + "&scantimeout=15.0"
                    + "&output=JSON"
                    + "&appid=LWUJE3-527ATY4RER"
                ).json()

                movie_json = movie_json["queryresult"]["pods"][0]["subpods"][0][
                    "plaintext"
                ]

                return movie_json

            except Exception as e:
                print("Wolfram Movie Data Error: ", query_title)
                checker.write("Wolfram Movie Data Error: " + query_title + "\n")
                checker.flush()
                # message = f"Error: {e}"
                # LOGGER.exception(message)
                return ""

    def __put_info_in_dict(self, movie_info_str):
        info_dict = {"title": "", "director": "", "release date": ""}
        info_str = movie_info_str.split("\n")
        for info in info_str:
            info_split = info.split(" | ")
            if len(info_split) == 2:
                info_dict[info_split[0]] = info_split[1]
            elif len(info_split) > 2:
                data_str = ""
                for i in range(1, len(info_split)):
                    data_str += info_split[i] + ", "
                info_dict[info_split[0][:-1]] = data_str[:-2]

        # turn date string into just year
        if info_dict["title"] == "Journey into Self":
            info_dict["release date"] = "1968"
        elif info_dict["director"] == "George Foster Platt, Nancy Hamilton":
            info_dict["title"] = "Helen Keller in Her Story"
            info_dict["director"] = "Nancy Hamilton"
            info_dict["release date"] = "June 15, 1954"
        else:
            date_str = info_dict["release date"]
            date_str_list = date_str.split(" (")
            info_dict["release date"] = date_str_list[0]
        """
        date_str_list = date_str.split(', ')
        if len(date_str_list) == 1:
            info_dict['release date'] = date_str_list[0][0:4]
        else:
            info_dict['release date'] = date_str_list[1][0:4]
        """
        return info_dict

    def __get_movie_noms_str(self, query_title, checker):
        try:
            noms_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_title
                + "&includepodid=CrossMovieData:AcademyAwardData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=LWUJE3-527ATY4RER"
            ).json()

            movie_noms_str = noms_json["queryresult"]["pods"][0]["subpods"][0][
                "plaintext"
            ]

            return movie_noms_str

        except Exception as e:
            # if query title resulted in error, try query title with film attached to title
            try:
                query_title_list = query_title.split("+(")
                query_title = query_title_list[0]
                query_title += "+film"

                movie_json = requests.get(
                    "https://api.wolframalpha.com/v2/query?input="
                    + query_title
                    + "&includepodid=BasicInformation:MovieData"
                    + "&format=plaintext"
                    + "&scantimeout=15.0"
                    + "&output=JSON"
                    + "&appid=LWUJE3-527ATY4RER"
                ).json()

                movie_json = movie_json["queryresult"]["pods"][0]["subpods"][0][
                    "plaintext"
                ]

                return movie_json

            except Exception as e:
                print("Wolfram Award Data Error: ", query_title)
                checker.write("Wolfram Award Data Error: " + query_title + "\n")
                checker.flush()
                # message = f"Error: {e}"
                # LOGGER.exception(message)
                return ""

    def __make_nom_list(self, nom_list_str):
        nom_list = list(nom_list_str.split("\n"))
        nom_list.remove(nom_list[0])

        return nom_list

    def __make_nom_list_of_objs(self, mov_noms_list):
        nom_list = []

        for nom_str in mov_noms_list:
            award_list = nom_str.split(" | ", 1)
            nom_list.append(self.__make_nomination_obj(award_list))

        return nom_list

    def __make_nomination_obj(self, nomination_str):
        nomination = Nomination(
            award_title=nomination_str[0].title(),
            names=list(nomination_str[1].split(" | ")),
        )

        nomination.save()

        return nomination

    def __find_wiki_page_title(self, query_title, checker):
        if query_title == "wallace+and+gromit+2005":
            query_title = "wallace+&+gromit:+the+curse+of+the+were+rabbit+film"
        elif query_title == "days+of+waiting":
            query_title = "Days of Waiting: The Life & Art of Estelle Ishigo"
        elif query_title == "all+the+king's+men+(1950+film)":
            query_title = "all+the+king's+men+(1949+film)"
        elif query_title == "black+fox+(1962+film)":
            query_title = "Black Fox: The Rise and Fall of Adolf Hitler"
        elif query_title == "quiet+please!+film":
            query_title = "Tom and Jerry filmography"
        elif query_title == "le+ciel+et+la+boue":
            query_title = "sky+above+and+mud+beneath"
        elif (
            query_title == "ryan+(film)"
            or query_title == "folies+bergere+de+paris+(1935+film)"
        ):
            query_title = query_title.replace("+", " ")
            page = wikipedia.search(query_title, results=2, suggestion=True)
            page_name = page[0][1]
            return page_name

        query_title = query_title.replace("+", " ")
        page = wikipedia.search(query_title, results=1, suggestion=True)
        if (
            query_title[:-5].lower() not in page[0][0].lower()
            and query_title.split(" (")[0].lower() not in page[0][0].lower()
        ):
            # print("query = ", query_title[:-5], ", page title: ", page[0][0])
            query_title = query_title[:-5]
            page = wikipedia.search(query_title, results=1, suggestion=True)
            if query_title[:-5].lower() not in page[0][0].lower():
                print("\nSTILL WRONG")
                checker.write(
                    "WIKI PAGE WRONG? query_title: "
                    + query_title
                    + ", page title: "
                    + page[0][0]
                    + "\n"
                )
                checker.flush()

        page_name = page[0][0]
        return page_name
        # wikipedia.set_lang("en")
        # wkpage = wikipedia.WikipediaPage(title=page).images
        # print(wkpage)

    def __get_wiki_img_link(self, page_title, checker):
        page_title = page_title.replace("&", "%26")
        response = requests.get(
            "https://en.wikipedia.org/w/api.php?action=query"
            + "&format=json"
            + "&formatversion=2"
            + "&prop=pageimages"
            + "&piprop=original"
            + "&pilicense=any"
            + "&titles="
            + page_title
        ).json()

        # TODO: WHAT IF NO IMG ON WIKIPEDIA
        try:
            img_link = response["query"]["pages"][0]["original"]["source"]
        except Exception as e:
            img_link = ""
            checker.write("NO IMG FOR PAGE: " + page_title + "\n")
            checker.flush()

        return img_link

    def __handle_edge_cases(self, query_title):
        if query_title == "the+secret+in+their+eyes+film":
            query_title = "the+secret+in+their+eyes+(2009+film)"
        elif query_title == "la+maison+en+petits+cubes+film":
            query_title = "the+house+of+small+cubes+film"
        elif query_title == "wallace+&+gromit:+the+curse+of+the+were+rabbit+film":
            query_title = "wallace+and+gromit+2005"
        elif query_title == "born+into+brothels+film":
            query_title = "born+into+brothels:+calcutta's+red+light+kids"
        elif query_title == "the+fog+of+war+film":
            query_title = "fog+of+war+film"
        elif query_title == "for+the+birds+(film)":
            query_title = "for+the+birds+(2001+film)"
        elif query_title == "u+571+(film)":
            query_title = "u-571+(film)"
        elif query_title == "legends+of+the+fall+film":
            query_title = "legends+of+the+fall+(1994+film)"
        elif query_title == "belle+epoque+(film)":
            query_title = "Belle+Epoque+(1992+film)"
        elif query_title == "reversal+of+fortune+film":
            query_title = "reversal+of+fortune+(1990+film)"
        elif query_title == "days+of+waiting:+the+life+&+art+of+estelle+ishigo+film":
            query_title = "days+of+waiting"
        elif query_title == "hôtel+terminus:+the+life+and+times+of+klaus+barbie+film":
            query_title = "hotel+terminus+(1988+film)"
        elif query_title == "the+assault+(film)":
            query_title = "the+assault+(1986+film)"
        elif query_title == "victor/victoria+film":
            query_title = "victor/victoria"
        elif query_title == "the+sand+castle+(film)":
            query_title = "the+sand+castle+(1977+film)"
        elif query_title == "the+omen+film":
            query_title = "the+omen+(1976+film)"
        elif query_title == "black+and+white+in+color+film":
            query_title = "black+and+white+in+color+(1977+film)"
        elif query_title == "the+bolero+film":
            query_title = "the+bolero+(1973+film)"
        elif query_title == "summer+of+'42+film":
            query_title = "summer+of+'42+(1971+film)"
        elif query_title == "the+garden+of+the+finzi+continis+(film)":
            query_title = "the+garden+of+the+finzi-continis+film"
        elif query_title == "is+it+always+right+to+be+right?+film":
            query_title = "is+it+always+right+to+be+right?+(1970+film)"
        elif query_title == "the+redwoods+film":
            query_title = "the+redwoods+(1967+film)"
        elif query_title == "the+producers+(1967+film)":
            query_title = "the+producers+1968+film"
        elif query_title == "the+box+(1967+film)":
            query_title = "the box film 1967"
        elif query_title == "america+america+film":
            query_title = "america+america+(1963+film)"
        elif query_title == "the+devil+and+daniel+webster+(film)":
            query_title = "all+that+money+can+buy+(1941+film)"
        elif query_title == "all+the+king's+men+(1949+film)":
            query_title = "all+the+king's+men+(1950+film)"
        elif query_title == "the+battle+of+midway+(film)":
            query_title = "the+battle+of+midway+(1942+film)"
        elif query_title == "bear+country+(film)":
            query_title = "bear+country+(1953+film)"
        elif query_title == "black+fox:+the+rise+and+fall+of+adolf+hitler+film":
            query_title = "black+fox+(1962+film)"
        elif query_title == "the+black+swan+(film)":
            query_title = "the black swan (1942 film)"
        elif query_title == "the+chicken+(film)":
            query_title = "le+poulet+(1965+film)"
        elif query_title == "december+7th:+the+movie+film":
            query_title = "december+7th+(1943+film)"
        elif query_title == "dumbo+film":
            query_title = "dumbo+(1941+film)"
        elif query_title == "folies+bergère+de+paris+film":
            query_title = "folies+bergere+de+paris+(1935+film)"
        elif query_title == "for+scent+imental+reasons+film":
            query_title = "for+scent-imental+reasons+film"
        elif query_title == "the+heiress+film":
            query_title = "the+heiress+(1949+film)"
        elif query_title == "helen+keller+in+her+story+film":
            query_title = "helen+keller+film"
        elif query_title == "hello,+frisco,+hello+film":
            query_title = "hello+frisco+hello+film"
        elif query_title == "the+hustler+(film)":
            query_title = "the+hustler+(1961+film)"
        elif query_title == "the+jazz+singer+film":
            query_title = "the+jazz+singer+(1927+film)"
        elif query_title == "jezebel+(1938+film)":
            query_title = "jezebel+film+(1938)"
        elif query_title == "joan+of+arc+(1948+film)":
            query_title = "joan+of+arc+(1949+film)"
        elif query_title == "the+little+orphan+film":
            query_title = "the+little+orphan+(1949+film)"
        elif query_title == "love+is+a+many+splendored+thing+(film)":
            query_title = "love+is+a+many-splendored+thing+(film)"
        elif query_title == "main+street+on+the+march!+film":
            query_title = "main+street+on+the+march!"
        elif query_title == "miracle+on+34th+street+film":
            query_title = "miracle+on+34th+street+(1947+film)"
        elif query_title == "nine+from+little+rock+film":
            query_title = "nine+from+little+rock+(1964+film)"
        elif query_title == "the+music+box+film":
            query_title = "the+music+box+film+(1932)"
        elif query_title == "samson+and+delilah+(1949+film)":
            query_title = "samson+and+delilah+(1950+film)"
        elif query_title == "the+search+film":
            query_title = "the+search+(1948)+film"
        elif query_title == "sky+above+and+mud+beneath+film":
            query_title = "le+ciel+et+la+boue"
        elif query_title == "some+like+it+hot+film":
            query_title = "some+like+it+hot+(1959+film)"
        elif query_title == "two+women+film":
            query_title = "la+ciociara"

        return query_title


if __name__ == "__main__":
    mov_controller = MovieController()
    mov_controller.post("parasite")
