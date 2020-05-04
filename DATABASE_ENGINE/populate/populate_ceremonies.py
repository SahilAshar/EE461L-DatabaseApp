import csv

import wikipedia

from controllers.ceremonies_controller import CeremoniesController


class PopulateCeremonies:
    def __init__(self):
        self.c_controller = CeremoniesController()

    def update_attributes(self):
        self.c_controller.update_attributes_for_all_years()

    def get_wiki_image_parser(self, search_term, ordinal_num):

        result = wikipedia.search(search_term, results=1)
        wikipedia.set_lang("en")
        wkpage = wikipedia.WikipediaPage(title=result[0])

        for image in wkpage.images:
            if ordinal_num in image:
                return image

        return ""

    def get_wiki_image_link(self):

        wiki_image = self.get_wiki_image_parser("91st Academy Awards", "91st")
        wiki_image_name = wiki_image.split("/")[-1]
        return wiki_image_name

    def print_ordinal_numbers(self):
        for i in range(1, 100):
            print(self.ordinal_string(i))

    def ordinal_string(self, i):
        if i >= 10 and i <= 20:
            suffix = "th"
        else:
            il = i % 10
            if il == 1:
                suffix = "st"
            elif il == 2:
                suffix = "nd"
            elif il == 3:
                suffix = "rd"
            else:
                suffix = "th"
        return str(i) + suffix

    def populate_wiki_images(self):

        with open(
            "DATABASE_ENGINE/populate/ceremonies_copy.csv", newline=""
        ) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row["Ceremony"], row["Year"])
                self.c_controller.post(row["Ceremony"], row["Year"])

    def populate(self):

        # TODO: error with 2006, will debug later
        for year in range(2007, 2017):
            self.c_controller.post(str(year))
            print("Completed : " + str(year))


if __name__ == "__main__":
    y = PopulateCeremonies()
    y.populate()
