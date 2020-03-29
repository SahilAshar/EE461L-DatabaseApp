from controllers.awards_controller import AwardController
from controllers.people_access_controller import PeopleAccessController


class PopulatePeople:
    def print_names(self):
        a_controller = AwardController()
        all_award_winners = a_controller.get_all_award_winners()

        for winner in all_award_winners:
            print(winner.name)

    def populate(self):
        pa_controller = PeopleAccessController()

        people_f = open("DATABASE_ENGINE/populate/people.txt", "r")

        people_list = people_f.readlines()

        for person in people_list:
            person = person.strip()
            person = person.lower()
            person = person.replace(" ", "+")
            pa_controller.post(person)
            print(person)
