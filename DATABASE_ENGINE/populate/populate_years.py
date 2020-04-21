import csv
import json

import requests
import wikipedia

from controllers.years_controller import YearController


class PopulateYears:
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
        y_controller = YearController()

        with open("DATABASE_ENGINE/populate/ceremonies.csv", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row["Ceremony"], row["Year"])
                y_controller.post(row["Ceremony"], row["Year"])

    def populate(self):
        y_controller = YearController()

        # TODO: error with 2006, will debug later
        for year in range(2007, 2017):
            y_controller.post(str(year))
            print("Completed : " + str(year))


if __name__ == "__main__":
    y = PopulateYears()
    y.populate()
