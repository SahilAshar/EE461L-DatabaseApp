import requests
import urllib.request


class person:
    def __init__(self):
        self.name = ""
        self.birthday = ""
        self.bio = ""
        self.awards = []

    # build personal info from resp strings
    def build_data(self, data_str, query_name):
        data_dict = {}
        data_dict["full name"] = ""
        data_dict["date of birth"] = ""

        data_list = list(data_str.split("\n"))
        for data in data_list:
            print(data)
            data_str_list = list(data.split(" | "))
            if len(data_str_list) == 2:
                data_dict[data_str_list[0]] = data_str_list[1]
            else:
                data_dict[data_str_list[0]] = ""

        if data_dict["full name"] == "":
            data_dict["full name"] = query_name.replace("+", " ")

        self.name = data_dict["full name"]
        self.birthday = data_dict["date of birth"]

    # set bio info
    def set_bio_data(self, bio_str):
        self.bio = bio_str


class award:
    def __init__(self):
        self.title = ""
        self.movie = ""
        self.year = ""

    # build award object from string
    # e.x. 'achievement in directing (winner) | 2020 (age: 50 years) | Parasite'
    def build_awards(self, award_str):
        award_list = list(award_str.split(" | "))
        self.title = award_list[0]
        self.movie = award_list[2]
        self.year = list(award_list[1].split(" "))[0]


def get_person_info(name):

    person_data = person()

    query_name = name.replace("-", "+")

    actor_data_info = requests.get(
        "https://api.wolframalpha.com/v2/query?input="
        + query_name
        + "&includepodid=BasicInformation:PeopleData&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()
    actor_data_str = actor_data_info["queryresult"]["pods"][0]["subpods"][0][
        "plaintext"
    ]
    print(actor_data_str)
    person_data.build_data(actor_data_str, query_name)

    actor_bio_info = requests.get(
        "https://api.wolframalpha.com/v2/query?input="
        + query_name
        + "&includepodid=WikipediaSummary:PeopleData&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()
    actor_bio_str = actor_bio_info["queryresult"]["pods"][0]["subpods"][0]["plaintext"]
    print(actor_bio_str)
    person_data.set_bio_data(actor_bio_str)

    # TODO: populate bio fields in person_data object
    actor_awards = requests.get(
        "https://api.wolframalpha.com/v2/query?input="
        + query_name
        + "&includepodid=CrossPeopleData:AcademyAwardData&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()

    # TODO: If numpods = 0, then they've won zero awards. Need to handle that case.

    print(actor_awards)
    # print(actor_awards["queryresult"]["pods"][0]["subpods"][0]["plaintext"])
    award_list_str = actor_awards["queryresult"]["pods"][0]["subpods"][0]["plaintext"]
    award_list = list(award_list_str.split("\n"))
    award_list.remove(award_list[0])
    award_list.remove(award_list[len(award_list) - 1])

    for award_str in award_list:
        new_award = award()
        new_award.build_awards(award_str)
        person_data.awards.append(new_award)

    print(str(person_data.awards))

    return person_data


if __name__ == "__main__":
    get_person_info("bong-joon-ho")
    get_person_info("rami-malek")
