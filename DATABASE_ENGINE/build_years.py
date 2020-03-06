import requests
import urllib.request


class year:
    def __init__(self):
        self.awards = []


class award:
    def __init__(self):
        self.title = ""
        self.nominees = []


class nominee:
    def __init__(self):
        self.song = ""
        self.name = ""
        self.movie = ""

    def build_nominee(self, nominee_info_str):
        self.movie = ""


def get_year_info():

    resp = requests.get(
        "https://api.wolframalpha.com/v2/query?input=Academy+award+2019&podstate=Result__More&podstate=Result__More&includepodid=Result&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()
    print(resp["queryresult"]["pods"][0]["subpods"][0]["plaintext"])


if __name__ == "__main__":
    get_year_info()
