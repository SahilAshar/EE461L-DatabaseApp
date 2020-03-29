import mongomock as mongomock

# had to install package mongomock for testing post

# test people controller
def test_people_get(app, make_pa_controller):
    #people list is list of all people that match query in get
    people_list = make_pa_controller.get("rami-malek")
    assert people_list[0].query_name == "rami+malek"


def test_people_post(app, make_pa_controller, make_person_inst):
    test_actor = make_pa_controller.post("rami-malek")
    assert test_actor.name == 'Rami Said Malek'
    assert test_actor.dob == 'Tuesday, May 12, 1981 (age: 38 years)'
    assert test_actor.bio == 'Rami Said Malek (Egyptian born May 12, 1981) is an American actor and producer. His breakthrough role was as computer hacker Elliot Alderson in the USA Network television series Mr. Robot (2015-2019), for which he received several accolades, including the 2016 Primetime Emmy Award for Outstanding Lead Actor in a Drama Series. In 2018, he portrayed rock singer and songwriter ...'
    assert test_actor.awards[0].movie == 'Bohemian Rhapsody'
    assert test_actor.awards[0].title == 'performance by an actor in a leading role (winner)'
    assert test_actor.awards[0].year == '2019'


# test about controller
def test_issues_init_works(new_issues):
    assert new_issues.total == 0


def test_commits_init_works(new_commits):
    assert new_commits.total == 0


def test_getting_issue_obj(make_about_controller):
    test_issue_array = make_about_controller.return_issue_obj()
    # test by adding up all issues and making sure it equals total commits
    # extra one for issue that has been closed
    total_issues = 1+test_issue_array.ablanchard10+test_issue_array.carosheehy+test_issue_array.natashalong+test_issue_array.Noah_Lisk+test_issue_array.Sahil_Ashar
    assert test_issue_array.total == total_issues


def test_getting_commits_obj(make_about_controller):
    test_commit_array = make_about_controller.return_commit_obj()
    #test by adding up all issues and making sure it equals total commits
    total_commits = test_commit_array.Sahil_Ashar+test_commit_array.Noah_Lisk+test_commit_array.natashalong+test_commit_array.carosheehy+test_commit_array.ablanchard10
    assert test_commit_array.total == total_commits


# test years controller
def test_year_get(app, make_years_controller):
    year_list = make_years_controller.get("1995")
    assert year_list.awards[0]['title'] == "best picture"
    assert year_list.awards[0]['nominees'][0]['name'] == "produced by Wendy Finerman, Steve Tisch and Steve Starkey"
    assert year_list.awards[0]['nominees'][0]['movie'] == "Forrest Gump"


def test_year_post(app, make_years_controller):
    test_yrobj = make_years_controller.post("1995")
    assert test_yrobj.year == '1995'
    assert test_yrobj.awards[0].title == 'best picture'
    assert test_yrobj.awards[0].nominees[0].movie == 'Forrest Gump'
    assert test_yrobj.awards[0].nominees[0].name == 'produced by Wendy Finerman, Steve Tisch and Steve Starkey'
    assert test_yrobj.awards[0].nominees[0].song == ''


"""
def test_ex(app):
    response = app.get("/")
    assert response.status_code == 200






def test_awards_in_certain_year(awards_for_1995):
    firstline = awards_for_1995
    firstline = firstline[0]
    assert str(firstline) == "best picture | Forrest Gump (produced by Wendy Finerman, Steve Tisch and Steve Starkey)"

"""