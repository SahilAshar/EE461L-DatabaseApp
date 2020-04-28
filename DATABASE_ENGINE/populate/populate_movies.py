import wikipedia
import logging
import time
from controllers.movies_controller import MoviesController

LOGGER = logging.getLogger(__name__)


class PopulateMovies:
    def __init__(self):
        self.mov_controller = MoviesController()

    def populate_movies(self):
        self.get_movie_list()

        movie_file = open("movies.txt", "r")
        movie_list = movie_file.readlines()

        low = 0
        high = 300
        for i in range(0, 5):
            for movie in movie_list[low:high]:
                movie = movie.rstrip("\n")
                movie = movie.strip()
                movie = movie.lower()
                movie = movie.replace(" ", "+")
                movie = movie.replace(",", "")
                print("Posting movie: ", movie)
                self.mov_controller.post(movie)

            low += 300
            if high >= len(movie_list):
                break
            elif high + 300 > len(movie_list):
                high = len(movie_list)
            else:
                high += 300

            time.sleep(360)

        movie_file.close()
        error_checker = open("movie_checker.txt", "r")
        contents = error_checker.read()
        print("\n\nError File:\n" + contents)

    def update_attributes(self):

        self.mov_controller.update_attributes_for_all_movies()

    # will get list of movies from wikipedia and populate txt file with titles
    def get_movie_list(self):
        wikipedia.set_lang("en")
        page_html_str = wikipedia.WikipediaPage(
            title="List of Academy Award-winning films"
        ).html()

        # parse through html to return list of table of all movies, each index is row of table
        table_html_list = self.__get_movie_table_html(page_html_str)

        # go through each position of table_html_list to return list of movie titles
        movie_list = self.__get_movie_list(table_html_list)
        # print(movie_list)

        # populate movies.txt file with movie_list
        self.__populate_txt_file(movie_list)

    def __get_movie_table_html(self, page_html_str):
        table_html = page_html_str.split("tbody")
        table_html = str(table_html[1])
        table_html = table_html.split("</tr>")
        table_html = table_html[1:-1]
        return table_html

    def __get_movie_list(self, table_html_list):
        movie_list = []
        for row in table_html_list:
            lines = row.split("<td>")
            line = lines[1]
            if "title=" in line:
                line_list = line.split("title=")
                line_list = line_list[1].split(">")
                title_with_quotes = line_list[0]
                title_with_quotes = title_with_quotes[1:-1]
                title_with_quotes = title_with_quotes.replace("&#39;", "'")
                title_with_quotes = title_with_quotes.replace("amp;", "")
                movie_list.append(title_with_quotes)

                # title_no_quotes_temp = line_list[1]
                # title_no_quotes_temp = title_no_quotes_temp.split("<")
                # title_no_quotes = title_no_quotes_temp[0]
                # if title_with_quotes != title_no_quotes:
                #     print(title_with_quotes +"   VS   "+ title_no_quotes)
            else:
                print("movie title not found from wiki table:", line)

        return movie_list

    def __populate_txt_file(self, movie_list):

        # movies_txt_file = open("movies.txt", "w")
        # for movie in movie_list:
        #     n = movies_txt_file.write(movie)
        #     print(n)
        # movies_txt_file.close()
        file_name = "movies.txt"
        with open(file_name, "a+") as file_object:
            file_object.truncate(0)
            appendEOL = False
            # Move read cursor to the start of file.
            file_object.seek(0)
            # Check if file is not empty
            data = file_object.read(100)
            if len(data) > 0:
                appendEOL = True
            # Iterate over each string in the list
            for line in movie_list:
                # If file is not empty then append '\n' before first line for
                # other lines always append '\n' before appending line
                if appendEOL == True:
                    file_object.write("\n")
                else:
                    appendEOL = True
                # Append element at the end of file
                file_object.write(line)

            file_object.close()
        # return outfile
