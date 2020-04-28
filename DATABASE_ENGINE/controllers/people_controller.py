import logging

from documents.people_documents import Person
from parsers.people_parser import PeopleParser

"""
    Design Choices
        - Seperates functions that make API calls and functions that parse
        strings for specifc values within a string
"""

LOGGER = logging.getLogger(__name__)


class PeopleController:
    def __init__(self):
        self.people_parser = PeopleParser()

    def post(self, name):
        actor = self.people_parser.parse(name)

        actor.save()

        # ! USED ONLY FOR TESTING
        return actor

    def get(self, query_name):

        # Query all Person documents for names that contain our
        # query_name string. Case insensive.
        query_name = query_name.replace("-", "+")

        matching_persons = Person.objects(query_name__icontains=query_name)

        if len(matching_persons) > 0:
            return matching_persons
        else:
            return False

    def get_paginated_people(self, page, view):

        if view == "descending":
            paginated_people = Person.objects.order_by("-name").paginate(
                page=page, per_page=9
            )
        elif view == "ascending":
            paginated_people = Person.objects.order_by("+name").paginate(
                page=page, per_page=9
            )

        return paginated_people

    def get_paginated_people_search(self, page, search):
        paginated_people = (
            Person.objects.search_text(search)
            .order_by("$text_score")
            .paginate(page=page, per_page=9)
        )

        return paginated_people

    def delete_blank_people(self):
        blank_people = Person.objects(name__iexact="")
        for person in blank_people:
            person.delete()

    def update_attributes_for_all_people(self):
        self.people_parser.update_attributes_for_all_people()


if __name__ == "__main__":
    p_controller = PeopleController()
    people = p_controller.get("rami-malek")
