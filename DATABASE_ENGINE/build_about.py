import os
import requests
from github import Github


GH_API_KEY = os.environ["GITHUB_API"]

g = Github(GH_API_KEY)
# Github Enterprise with custom hostname


class commits:
    def __init__(self):
        self.total = 0
        self.Sahil_Ashar = 0
        self.ablanchard10 = 0
        self.Noah_Lisk = 0
        self.natashalong = 0
        self.carosheehy = 0

    def build_commit(self):

        repo = g.get_repo("SahilAshar/EE461L-DatabaseApp")
        # contents = repo.get_clones_traffic()
        # contents has total number of commits and also splits them up by day
        contents = repo.get_clones_traffic()

        self.total = contents["count"]

        commits = requests.get(
            "https://api.github.com/repos/SahilAshar/EE461L-DatabaseApp/commits"
        ).json()

        commitdict = {}
        commitdict["natashalong"] = 0
        commitdict["Sahil Ashar"] = 0
        commitdict["Noah Lisk"] = 0
        commitdict["carosheehy"] = 0
        commitdict["Austin_Blanchard"] = 0
        for commit in commits:
            commitdict[commit["commit"]["author"]["name"]] = (
                commitdict[commit["commit"]["author"]["name"]] + 1
            )
        print(commitdict)

        self.natashalong = commitdict["natashalong"]
        self.Sahil_Ashar = commitdict["Sahil Ashar"]
        self.Noah_Lisk = commitdict["Noah Lisk"]
        self.carosheehy = commitdict["carosheehy"]
        self.ablanchard10 = commitdict["Austin_Blanchard"]


class issues:
    def __init__(self):
        self.total = 0
        self.Sahil_Ashar = 0
        self.ablanchard10 = 0
        self.Noah_Lisk = 0
        self.natashalong = 0
        self.carosheehy = 0

    def build_issue(self):

        issues = requests.get(
            "https://api.github.com/repos/SahilAshar/EE461L-DatabaseApp/issues"
        ).json()
        # print(issues[0]["number"])

        self.total = issues[0]["number"]

        issuedict = {}
        issuedict["natashalong"] = 0
        issuedict["SahilAshar"] = 0
        issuedict["noahlisk"] = 0
        issuedict["carosheehy"] = 0
        issuedict["ablanchard10"] = 0
        for issue in issues:
            issuedict[issue["assignee"]["login"]] = (
                issuedict[issue["assignee"]["login"]] + 1
            )

        self.natashalong = issuedict["natashalong"]
        self.Sahil_Ashar = issuedict["SahilAshar"]
        self.Noah_Lisk = issuedict["noahlisk"]
        self.carosheehy = issuedict["carosheehy"]
        self.ablanchard10 = issuedict["ablanchard10"]


def return_issue_obj():
    new_issue = issues()
    new_issue.build_issue()
    return new_issue


def return_commit_obj():
    new_commit = commits()
    new_commit.build_commit()
    return new_commit
