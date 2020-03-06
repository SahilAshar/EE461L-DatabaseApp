import requests
import urllib.request


class year:
    def __init__(self):
        self.awards = []


class award:
    def __init__(self):
        self.title = ""
        self.nominees = []

    def build_award(self, award_info_str):
        new_nominee = nominee()
        award_info_list = list(award_info_str.split(" | "))
        self.title = award_info_list[0]
        new_nominee.build_nominee(award_info_list[1], self.title)
        self.nominees.append(new_nominee)


class nominee:
    def __init__(self):
        self.song = ""
        self.name = ""
        self.movie = ""

    def build_nominee(self, nominee_info_str, title):
        if title == "best motion picture" or title == "best picture":
            nominee_info_list = nominee_info_str.split(" (")
            self.movie = nominee_info_list[0]
            # self.name = nominee_info_list[1].replace("(", "")
            self.name = nominee_info_list[1].replace(")", "")
        elif (
            title == "achievement in music written for motion pictures (original song)"
        ):
            nominee_info_list = nominee_info_str.split(" for ")
            self.name = nominee_info_list[0]
            song_info_list = nominee_info_list[1].split(" in ")
            self.song = song_info_list[0]
            self.movie = song_info_list[1]
        elif title == "foreign language film":
            self.movie = nominee_info_str
        else:
            nominee_info_list = nominee_info_str.split(" in ")
            if len(nominee_info_list) < 2:
                nominee_info_list = nominee_info_str.split(" for ")
            if len(nominee_info_list) < 2:
                self.name = nominee_info_list[0]
            else:
                self.name = nominee_info_list[0]
                self.movie = nominee_info_list[1]


def get_year_info(year_num):

    new_year = year()

    all_awards = requests.get(
        "https://api.wolframalpha.com/v2/query?input=Academy+award+"
        + str(year_num)
        + "&podstate=Result__More&podstate=Result__More&includepodid=Result&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()
    all_awards_str = all_awards["queryresult"]["pods"][0]["subpods"][0]["plaintext"]
    print(all_awards_str)

    all_awards_list = all_awards_str.split("\n")

    for award_list_str in all_awards_list:
        new_award = award()
        new_award.build_award(award_list_str)
        new_year.awards.append(new_award)

    return new_year.awards


if __name__ == "__main__":
    get_year_info(1995)
