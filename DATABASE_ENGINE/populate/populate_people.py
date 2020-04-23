from controllers.awards_controller import AwardController
from controllers.people_access_controller import PeopleAccessController
from controllers.movie_controller import MovieController


class PopulatePeople:
    def print_names(self):
        m_controller = MovieController()
        all_nomination_objects = m_controller.get_all_nominations()

        people_f = open("DATABASE_ENGINE/populate/people.txt", "w")

        for nomination in all_nomination_objects:
            for name in nomination.names:
                people_f.write(name + "\n")

        people_f.close()

    def delete(self):
        pa_controller = PeopleAccessController()
        pa_controller.delete_blank_people()

    def populate(self):
        pa_controller = PeopleAccessController()

        people_f = open("DATABASE_ENGINE/populate/people_txt/people_z.txt", "r")

        people_list = people_f.readlines()

        for person in people_list:
            person = person.strip()
            person = person.lower()
            person = person.replace(" ", "+")
            pa_controller.post(person)
            print(person)
