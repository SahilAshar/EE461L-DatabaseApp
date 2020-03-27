import os
import pytest
from flask import Flask

#from DATABASE_ENGINE.build_about import issues
#from DATABASE_ENGINE.build_about import commits

from DATABASE_ENGINE.build_years import get_year_info
#from DATABASE_ENGINE.main import root
from DATABASE_ENGINE.controllers.database_controller import initialize_db

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


@pytest.fixture
def make_pa_controller():
    test_pacontroller = PeopleAccessController()
    return test_pacontroller

@pytest.fixture
def make_person_inst():
    me = Person(
        query_name="austin+blanchard",
        name="austin blanchard",
        dob="Monday, February 27, 1999 (age: 21 years)",
        bio="I am lit",
        awards=["not yet"]
    )
    return me

"""
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('flask_test.cfg')

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture()
def new_issues():
    test_issues = issues()
    return test_issues


@pytest.fixture()
def new_commits():
    test_commits = commits()
    return test_commits
"""


@pytest.fixture()
def awards_for_1995():
    awards = get_year_info(1995)
    print(awards[0].nominees)
    return awards



