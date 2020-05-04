import logging

from documents.movies_documents import Movie, Nomination
from parsers.movies_parser import MoviesParser


LOGGER = logging.getLogger(__name__)


class MoviesController:
    def __init__(self):
        self.movies_parser = MoviesParser()

    def post(self, title):
        movie = self.movies_parser.parse(title)

        movie.save()

        return movie

    def get(self, query_title):

        try:
            movies_found = Movie.objects(link_title__iexact=query_title).get()
            return movies_found
        except Exception as e:
            message = f"Error: {e}"
            LOGGER.exception(message)
            return False

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

    def get_paginated_movies_search(self, page, search):

        paginated_movies = (
            Movie.objects.search_text(search)
            .order_by("$text_score")
            .paginate(page=page, per_page=9)
        )

        return paginated_movies

    # ! Temp function for instance population
    def get_all_nominations(self):
        all_nomination_objects = Nomination.objects()

        return all_nomination_objects

    def update_attributes_for_all_movies(self):
        self.movies_parser.update_attributes_for_all_movies()


if __name__ == "__main__":
    m_controller = MoviesController()
    m_controller.post("parasite")
