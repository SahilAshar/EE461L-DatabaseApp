import requests
import urllib.request


# winner object class will build an object
# based on the input string passed in fron the best_actor
# API call
class award_winner:
    def __init__(self):
        self.name = ""
        self.movie = ""
        self.year = ""

    # example input : '2020 | Joaquin Phoenix in Joker'
    def build_winner(self, winner_str):
        li = []

        # gets the year
        li = list(winner_str.split(" | "))

        # gets the movie and name
        li2 = li[1].split(" in ")

        self.name = li2[0]
        self.movie = li2[1]
        self.year = li[0]


class award:
    def __init__(self):
        self.title = ""
        self.winners = []


def get_best_actor_list():
    # Best Actor API Call Processing
    title = "Actor in a Leading Role"

    # TODO: handle Results_more
    resp = requests.get(
        "https://api.wolframalpha.com/v2/query?input=best+actor&format=plaintext&output=JSON&appid=9U487H-VALXT3HLLQ"
    ).json()
    recalculate_link = resp["queryresult"]["recalculate"]
    print(recalculate_link)

    # TODO: Handle case where there is no recalculate link
    if recalculate_link != "":
        # print("here")
        resp = requests.get(recalculate_link).json()
        resp_winner_str = resp["queryresult"]["pods"][0]["subpods"][0]["plaintext"]
        resp_winner_list = list(resp_winner_str.split("\n"))
        resp_winner_list.remove(resp_winner_list[0])
        resp_winner_list.remove(resp_winner_list[len(resp_winner_list) - 1])

        best_actor_award = award()
        best_actor_award.title = title
        # best_actor_award.winners = [award_winner()] * len(resp_winner_list)

        # for each winner string in the response list
        # instantiate a new actor, build the actor, append to award list
        for winner in resp_winner_list:
            actor = award_winner()
            actor.build_winner(winner)
            best_actor_award.winners.append(actor)

        print(str(best_actor_award.winners))

        return best_actor_award
    else:
        print("edge case")


if __name__ == "__main__":
    get_best_actor_list()
