
def test_people_get(app, make_pa_controller):
    list = make_pa_controller.get("rami-malek")
    assert list[0].query_name == "rami+malek"


def test_



"""
def test_ex(app):
    response = app.get("/")
    assert response.status_code == 200



def test_issues_init_works(new_issues):
    assert new_issues.total == 0



def test_awards_in_certain_year(awards_for_1995):
    firstline = awards_for_1995
    firstline = firstline[0]
    assert str(firstline) == "best picture | Forrest Gump (produced by Wendy Finerman, Steve Tisch and Steve Starkey)"

"""