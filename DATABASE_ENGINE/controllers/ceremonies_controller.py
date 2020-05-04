import logging

from documents.ceremonies_documents import Year
from parsers.ceremonies_parser import CeremoniesParser

LOGGER = logging.getLogger(__name__)

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""


class CeremoniesController:
    def __init__(self):
        self.ceremonies_parser = CeremoniesParser()

    # TODO: Make POST uneccesary by abstracting Award logic elsewhere
    def post(self, ceremony_name, year):

        year = self.ceremonies_parser.parse(ceremony_name, year)

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

    def update_attributes_for_all_years(self):
        self.ceremonies_parser.update_attributes_for_all_years()


if __name__ == "__main__":
    c_controller = CeremoniesController()
    c_controller.post(1995)
    # year = y_controller.get(1995)
