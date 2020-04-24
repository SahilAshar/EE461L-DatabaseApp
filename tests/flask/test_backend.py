
# test people controller
import pytest


def test_people_get(app, make_pa_controller):
    #people list is list of all people that match query in get
    people_list = make_pa_controller.get("rami-malek")
    assert people_list[0].query_name == "rami+malek"


def test_people_get_fail(app, make_pa_controller):
    people_list = make_pa_controller.get("austin-blanchard")
    assert len(people_list) == 0


def test_people_post(app, make_pa_controller, make_person_inst):
    test_actor = make_pa_controller.post("rami-malek")
    assert test_actor.name == 'Rami Said Malek'
    assert test_actor.dob == 'Tuesday, May 12, 1981 (age: 38 years)'
    assert test_actor.bio == 'Rami Said Malek (Egyptian born May 12, 1981) is an American actor and producer. His breakthrough role was as computer hacker Elliot Alderson in the USA Network television series Mr. Robot (2015-2019), for which he received several accolades, including the 2016 Primetime Emmy Award for Outstanding Lead Actor in a Drama Series. In 2018, he portrayed rock singer and songwriter ...'
    assert test_actor.awards[0].movie == 'Bohemian Rhapsody'
    assert test_actor.awards[0].title == 'performance by an actor in a leading role (winner)'
    assert test_actor.awards[0].year == '2019'


def test_issues_init_works(new_issues):
    assert new_issues.total == 0


def test_commits_init_works(new_commits):
    assert new_commits.total == 0


def test_getting_issue_obj(make_about_controller):
    test_issue_array = make_about_controller.return_issue_obj()
    # test by adding up all issues and making sure it equals total commits
    # extra 16 for issues that have been closed
    total_issues = test_issue_array.ablanchard10+test_issue_array.carosheehy+test_issue_array.natashalong+test_issue_array.Noah_Lisk+test_issue_array.Sahil_Ashar
    assert test_issue_array.total == total_issues+16


def test_getting_commits_obj(make_about_controller):
    test_commit_array = make_about_controller.return_commit_obj()
    #test by adding up all issues and making sure it equals total commits
    total_commits = test_commit_array.Sahil_Ashar+test_commit_array.Noah_Lisk+test_commit_array.natashalong+test_commit_array.carosheehy+test_commit_array.ablanchard10
    assert test_commit_array.total == total_commits


# test years controller
def test_year_get(app, make_years_controller):
    year_list = make_years_controller.get("1996")
    assert year_list.awards[0]['title'] == "best picture"
    assert year_list.awards[0]['nominees'][0]['name'] == "produced by Mel Gibson, Alan Ladd, Jr. and Bruce Davey"
    assert year_list.awards[0]['nominees'][0]['movie'] == "Braveheart"


def test_year_get_fail(app, make_years_controller):
    with pytest.raises(Exception):
        assert make_years_controller.get('2022')


def test_year_post(app, make_years_controller):
    test_yrobj = make_years_controller.post("1995")
    assert test_yrobj.year == '1995'
    assert test_yrobj.awards[0].title == 'best picture'
    assert test_yrobj.awards[0].nominees[0].movie == 'Forrest Gump'
    assert test_yrobj.awards[0].nominees[0].name == 'produced by Wendy Finerman, Steve Tisch and Steve Starkey'
    assert test_yrobj.awards[0].nominees[0].song == ''


# test awards controller
def test_award_get(app, make_awards_controller):
    test_bestpiclist = make_awards_controller.get('best-picture')
    assert test_bestpiclist.title == 'best picture'
    assert test_bestpiclist.winners[0].name == 'Parasite (produced by Sin-ae Kwak and Bong Joon-ho)'
    assert test_bestpiclist.winners[0].movie == ''
    assert test_bestpiclist.winners[0].song == ''
    assert test_bestpiclist.winners[0].year == '2020'

# test movies controller
def test_movie_get(app, make_movies_controller):
    test_movielist = make_movies_controller.get("parasite+(2019+film)")
    assert test_movielist[0].title == 'Parasite'
    assert test_movielist[0].year == 'October 11, 2019'
    assert test_movielist[0].link_title == 'parasite'
    assert test_movielist[0].image_link == 'https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png'
    assert test_movielist[0].director == 'Bong Joon-ho'
    assert len(test_movielist[0].nominations) == 6
    assert test_movielist[0].nominations[0].award_title == 'Achievement In Directing (Winner)'
    assert len(test_movielist[0].nominations[0].names) == 1
    assert test_movielist[0].nominations[0].names[0] == 'Bong Joon-ho'

def test_movie_get_fail(app, make_movies_controller):
    test_movielist = make_movies_controller.get("yo what it do")
    assert len(test_movielist) == 0

def test_movie_post(app, make_movies_controller):
    test_movie = make_movies_controller.post("parasite+(2019+film)")
    assert test_movie.title == 'Parasite'
    assert test_movie.year == 'October 11, 2019'
    assert test_movie.link_title == 'parasite'
    assert test_movie.image_link == 'https://upload.wikimedia.org/wikipedia/en/5/53/Parasite_%282019_film%29.png'
    assert test_movie.director == 'Bong Joon-ho'
    assert len(test_movie.nominations) == 6
    assert test_movie.nominations[0].award_title == 'Achievement In Directing (Winner)'
    assert len(test_movie.nominations[0].names) == 1
    assert test_movie.nominations[0].names[0] == 'Bong Joon-ho'