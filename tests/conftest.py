import os
import pytest
from flask import Flask

from DATABASE_ENGINE.build_about import issues
from DATABASE_ENGINE.build_about import commits

from DATABASE_ENGINE.build_years import get_year_info
from DATABASE_ENGINE.main import root


"""
from example_app import create_app
"""
@pytest.fixture
def app():
    app = Flask(__name__)
    return app

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
"""

@pytest.fixture()
def new_issues():
    test_issues = issues()
    return test_issues

"""
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



