import os
import tempfile
import pytest


from DATABASE_ENGINE.build_about import issues
from DATABASE_ENGINE.build_about import commits
from DATABASE_ENGINE.main import app
from DATABASE_ENGINE.build_years import get_year_info
from tests import conftest


def test_ex(app):
    response = app.get("/")
    assert response.status_code == 200



def test_issues_init_works(new_issues):
    assert new_issues.total == 0



def test_awards_in_certain_year(awards_for_1995):
    firstline = awards_for_1995
    firstline = firstline[0]
    assert str(firstline) == "best picture | Forrest Gump (produced by Wendy Finerman, Steve Tisch and Steve Starkey)"
