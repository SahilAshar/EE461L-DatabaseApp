from controllers.people_access_controller import PeopleAccessController
from controllers.movie_controller import MovieController

import os


class PopulatePeople:
    def print_names(self):
        m_controller = MovieController()
        all_nomination_objects = m_controller.get_all_nominations()

        people_f = open("DATABASE_ENGINE/populate/people.txt", "w")

        for nomination in all_nomination_objects:
            for name in nomination.names:
                people_f.write(name + "\n")

        people_f.close()

    def update_attributes(self):
        pa_controller = PeopleAccessController()
        pa_controller.update_attributes_for_all_people()

    def delete(self):
        pa_controller = PeopleAccessController()
        pa_controller.delete_blank_people()

    def populate(self):
        pa_controller = PeopleAccessController()

        # people_file_list = [
        #     "people_a.txt",
        #     "people_b.txt",
        #     "people_c.txt",
        #     "people_d.txt",
        #     "people_e.txt",
        #     "people_f.txt",
        #     "people_g.txt",
        #     "people_h.txt",
        #     "people_i.txt",
        #     "people_j.txt",
        #     "people_k.txt",
        #     "people_l.txt",
        #     "people_m.txt",
        #     "people_n.txt",
        #     "people_o.txt",
        #     "people_p.txt",
        #     "people_q.txt",
        #     "people_r.txt",
        #     "people_s.txt",
        #     "people_t.txt",
        #     "people_u.txt",
        #     "people_v.txt",
        #     "people_w.txt",
        #     "people_y.txt",
        #     "people_z.txt",
        # ]

        people_file_list = ["all people.txt"]

        for people_file_name in people_file_list:

            # os.system("pwd")
            # people_f = open("DATABASE_ENGINE/populate/people_txt/people_a.txt", "r")

            # people_f = open(
            #     "DATABASE_ENGINE/populate/people_txt/" + people_file_name, "r"
            # )

            people_f = open("populate/people_txt/" + people_file_name, "r")

            people_list = people_f.readlines()

            for person in people_list:
                person = person.strip()
                person = person.lower()
                person = person.replace(" ", "+")

                if pa_controller.get(person) is False:
                    pa_controller.post(person)
                    print(person)
                else:
                    print(person + "already exists")
                    continue
