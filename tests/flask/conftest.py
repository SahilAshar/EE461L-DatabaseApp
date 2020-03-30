import os
import pytest
from flask import Flask

from DATABASE_ENGINE.controllers.about_controller import issues
from DATABASE_ENGINE.controllers.about_controller import commits
from DATABASE_ENGINE.controllers.about_controller import AboutController

from DATABASE_ENGINE.controllers.years_controller import YearController

from DATABASE_ENGINE.controllers.database_controller import initialize_db

from DATABASE_ENGINE.controllers.awards_controller import AwardController

from DATABASE_ENGINE.controllers.people_access_controller import PeopleAccessController
from DATABASE_ENGINE.controllers.people_access_controller import Person

#python -m pytest tests/    --- to run test from root folder.2..


"""
from example_app import create_app
"""


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["MONGODB_SETTINGS"] = {
        "db": "omdb",
        "host": "mongodb+srv://sashar:qwerty12345@cluster0-0jhiw.gcp.mongodb.net/omdb?retryWrites=true&w=majority",
    }
    initialize_db(app)
    return app

# make people controller
@pytest.fixture
def make_pa_controller():
    test_pacontroller = PeopleAccessController()
    return test_pacontroller

# rami malek Person object for testing
@pytest.fixture
def make_person_inst():
    me = Person(
        query_name="rami+malek",
        name="rami malek",
        dob="Tuesday, May 12, 1981 (age: 38 years)",
        bio="RAMI SAID MALEK (EGYPTIAN BORN MAY 12, 1981) IS AN AMERICAN ACTOR AND PRODUCER. HIS BREAKTHROUGH ROLE WAS AS COMPUTER HACKER ELLIOT ALDERSON IN THE USA NETWORK TELEVISION SERIES MR. ROBOT (2015-2019), FOR WHICH HE RECEIVED SEVERAL ACCOLADES, INCLUDING THE 2016 PRIMETIME EMMY AWARD FOR OUTSTANDING LEAD ACTOR IN A DRAMA SERIES. IN 2018, HE PORTRAYED ROCK SINGER AND SONGWRITER ...",
        awards=["not yet"]
    )
    return me

#make stuff to test about
@pytest.fixture()
def new_issues():
    test_issues = issues()
    return test_issues


@pytest.fixture()
def new_commits():
    test_commits = commits()
    return test_commits


@pytest.fixture()
def make_about_controller():
    test_abtcontroller = AboutController()
    return test_abtcontroller


# make years controller
@pytest.fixture()
def make_years_controller():
    test_yrcontroller = YearController()
    return test_yrcontroller


# make awards controller
@pytest.fixture()
def make_awards_controller():
    test_awardcontroller = AwardController()
    return test_awardcontroller

