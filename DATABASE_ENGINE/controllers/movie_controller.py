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
    title = db.StringField()
    director = db.StringField()
    year = db.StringField()
    image_link = db.StringField()
    nominations = db.ListField(db.ReferenceField(Nomination))


class MovieController:
    def post(self, title):
        query_title = title.replace("-", "+")
        query_title += "+movie"

        # Return string with movie title, director, and year and other info
        movie_info_str = self.__get_movie_info_str(query_title)

        # return dict with title, dir, yr from movie_info_str // dict helpful bc each index can be label from json
        movie_info_dict = self.__put_info_in_dict(movie_info_str)

        # now will get image data from wikipedia api
        wkpage_title_str = self.__find_wiki_page_title(query_title)

        wiki_img_link_str = self.__get_wiki_img_link(wkpage_title_str)


        mov = Movie(
            query_title=query_title,
            title=movie_info_dict['title'],
            director=movie_info_dict['director'],
            year=movie_info_dict['release date'],
            image_link=wiki_img_link_str,
        )

        mov.save()

        # get string with all awards nominations
        mov_noms_str = self.__get_movie_noms_str(query_title)

        # now make string into list of nomination strings
        mov_noms_list = self.__make_nom_list(mov_noms_str)

        # turn mov_noms_list into list of nomination objects and place into movie
        mov.nominations = self.__make_nom_list_of_objs(mov_noms_list)

        mov.save()

        print(Movie.objects.count())

    def get(self, title):

        # format title to be same as query title in post
        query_title = title.replace("-", "+")

        # now find movies in db that have same query_title as movie you want to get
        movies_found = Movie.objects(query_title__icontains=query_title)

        # movies_found should only have length 1 if populated correctly so will just return 1 movie
        return movies_found

    def __get_movie_info_str(self, query_title):
        try:
            movie_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_title
                + "&includepodid=BasicInformation:MovieData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=9U487H-VALXT3HLLQ"
            ).json()

            movie_json = movie_json["queryresult"]["pods"][0]["subpods"][0]["plaintext"]

            return movie_json
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __put_info_in_dict(self, movie_info_str):
        info_dict = {'title': "", 'director': "", 'release date': ""}

        info_str = movie_info_str.split('\n')
        for info in info_str:
            info_split = info.split(' | ')
            if len(info_split) == 2:
                info_dict[info_split[0]] = info_split[1]

        # turn date string into just year
        date_str = info_dict['release date']
        date_str = date_str.split(', ')
        info_dict['release date'] = date_str[1][0:4]

        return info_dict

    def __get_movie_noms_str(self, query_title):
        try:
            noms_json = requests.get(
                "https://api.wolframalpha.com/v2/query?input="
                + query_title
                + "&includepodid=CrossMovieData:AcademyAwardData"
                + "&format=plaintext"
                + "&scantimeout=15.0"
                + "&output=JSON"
                + "&appid=9U487H-VALXT3HLLQ"
            ).json()

            movie_noms_str = noms_json["queryresult"]["pods"][0]["subpods"][0]["plaintext"]

            return movie_noms_str

        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return ""

    def __make_nom_list(self, nom_list_str):
        nom_list = list(nom_list_str.split('\n'))
        nom_list.remove(nom_list[0])

        return nom_list

    def __make_nom_list_of_objs(self, mov_noms_list):
        nom_list = []

        for nom_str in mov_noms_list:
            award_list = nom_str.split(' | ', 1)
            nom_list.append(self.__make_nomination_obj(award_list))

        return nom_list

    def __make_nomination_obj(self, nomination_str):
        nomination = Nomination(
            award_title=nomination_str[0].title(),
            names=list(nomination_str[1].split(' | '))
        )

        nomination.save()

        return nomination

    def __find_wiki_page_title(self, query_title):
        query_title = query_title.replace("+", " ")
        page = wikipedia.search(query_title, results=1)
        return page[0]
        # wikipedia.set_lang("en")
        # wkpage = wikipedia.WikipediaPage(title=page).images
        # print(wkpage)

    def __get_wiki_img_link(self, page_title):
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

        img_link = response['query']['pages'][0]['original']['source']
        return img_link

if __name__ == "__main__":
    mov_controller = MovieController()
    mov_controller.post("parasite")