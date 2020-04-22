import datetime


from flask import Flask, redirect, render_template, url_for, request
from flask_mongoengine import MongoEngine

from controllers.about_controller import AboutController
from controllers.awards_controller import AwardController
from controllers.database_controller import initialize_db
from controllers.people_access_controller import PeopleAccessController
from controllers.years_controller import YearController
from controllers.movie_controller import MovieController

from populate.populate_years import PopulateYears
from populate.populate_people import PopulatePeople
from populate.populate_movies import PopulateMovies


app = Flask(__name__)

app.config["DEBUG"] = True
app.config["MONGODB_SETTINGS"] = {
    "db": "omdb",
    "host": "mongodb+srv://sashar:qwerty12345@cluster0-0jhiw.gcp.mongodb.net/omdb?retryWrites=true&w=majority",
}

# Initializing DB separately, best practice for application factories
initialize_db(app)


@app.route("/")
@app.route("/home")
def root():

    return render_template("index.html")


@app.route("/about")
def about():

    about_controller = AboutController()

    issues_obj = about_controller.return_issue_obj()
    commits_obj = about_controller.return_commit_obj()

    return render_template("about.html", issues=issues_obj, commits=commits_obj)


# TODO: this is a janky way of handling pagination, pls fix @Sahil
@app.route("/years/")
@app.route("/years/page=<page>/")
@app.route("/years/page=<page>/view=<view>")
def year_root(page=1, view="descending"):

    page = int(page)
    y_controller = YearController()
    paginated_years = y_controller.get_paginated_years(page, view)

    return render_template("years.html", paginated_years=paginated_years, view=view)


@app.route("/years/search_helper", methods=["POST"])
def year_search_helper():
    return redirect(url_for("year_search", search=request.form["search_text"]))


@app.route("/years/filter_helper", methods=["POST"])
def year_filter_helper():
    return redirect(url_for("year_root", page=1, view=request.form["radio"]))


# TODO: this is a janky way of handling pagination, pls fix @Sahil
@app.route("/years/search=<search>")
@app.route("/years/search=<search>/page=<page>")
def year_search(page=1, search=None):

    if search is None:
        redirect(url_for("year_search", search=request.form["search_text"]))

    page = int(page)
    y_controller = YearController()
    paginated_years = y_controller.get_paginated_years_search(page, search)

    return render_template("years.html", paginated_years=paginated_years)


@app.route("/years/<ceremony_name>/")
def year_instance(ceremony_name=None):

    y_controller = YearController()
    year_obj = y_controller.get(ceremony_name)

    return render_template("years_instance.html", year=year_obj, awards=year_obj.awards)


@app.route("/years/num/<year_num>/")
# def ceremony_from_year_num(ceremony, year_num=None):
def ceremony_from_year_num(year_num=None):
    y_controller = YearController()
    ceremony_name = y_controller.get_ceremony_name_by_year(year_num)

    return redirect(url_for("year_instance", ceremony_name=ceremony_name))

    # return render_template("years_instance.html", year=year_obj, awards=year_obj.awards)


# TODO : This works(?) Need to make this an actual post request
# But this proves I can create actual controllers that can link
@app.route("/years/new/<year>/")
def new_year(year):

    y_controller = YearController()
    y_controller.post(year)

    return redirect("/years/" + year + "/")


# ! Temporary, do not use in production
@app.route("/years/populate")
def populate_years():

    y = PopulateYears()

    # y.get_wiki_image_link()
    # y.print_ordinal_numbers()
    # y.populate()
    y.populate_wiki_images()

    return redirect("/years/")


@app.route("/awards/")
@app.route("/awards/page=<page>")
def award_root(page=1):

    page = int(page)
    a_controller = AwardController()
    paginated_awards = a_controller.get_paginated_full_awards(page)

    return render_template("awards.html", paginated_awards=paginated_awards)


@app.route("/awards/<award>/")
def award_instance(award):

    a_controller = AwardController()
    awards = a_controller.get(award)

    return render_template("awards_instance.html", awards=awards)


# TODO : This works(?) Need to make this an actual post request
# But this proves I can create actual controllers that can link
@app.route("/awards/new/update-all")
def update_all_awards():
    a_controller = AwardController()
    a_controller.post()

    return redirect("/awards/")


# TODO: this is a janky way of handling pagination, pls fix @Sahil
@app.route("/people/")
@app.route("/people/page=<page>")
@app.route("/people/page=<page>/view=<view>")
def people_root(page=1, view="ascending"):

    page = int(page)
    pa_controller = PeopleAccessController()
    paginated_people = pa_controller.get_paginated_people(page, view)

    return render_template("people.html", paginated_people=paginated_people, view=view)


@app.route("/people/filter_helper", methods=["POST"])
def people_filter_helper():
    return redirect(url_for("people_root", page=1, view=request.form["radio"]))


@app.route("/people/search_helper", methods=["POST"])
def people_search_helper():
    return redirect(url_for("people_search", search=request.form["search_text"]))


@app.route("/people/search=<search>")
@app.route("/people/search=<search>/page=<page>")
def people_search(page=1, search=None):

    # if search == "" or search is None:
    #     redirect(url_for("people_search", page=1, search=request.form["search_text"]))

    page = int(page)
    pa_controller = PeopleAccessController()
    paginated_people = pa_controller.get_paginated_people_search(page, search)

    return render_template("people.html", paginated_people=paginated_people)


@app.route("/people/<person>/")
def people_instance(person=None):

    pa_controller = PeopleAccessController()
    people = pa_controller.get(person)

    print(len(people))
    print(people[0])

    return render_template("people_instance.html", people=people[0])


# TODO : This works(?) Need to make this an actual post request
# But this proves I can create actual controllers that can link
@app.route("/people/new/<person>/")
def new_person(person):
    pa_controller = PeopleAccessController()
    pa_controller.post(person)

    return redirect("/people/" + person + "/")


# ! Temporary, do not use in production
@app.route("/people/populate")
def populate_people():

    p = PopulatePeople()

    # p.print_names()
    p.populate()

    return redirect("/people/")


# TODO: this is a janky way of handling pagination, pls fix @Sahil
@app.route("/movies/")
@app.route("/movies/page=<page>")
@app.route("/movies/page=<page>/view=<view>")
def movies_root(page=1, view="ascending"):

    page = int(page)
    m_controller = MovieController()
    paginated_movies = m_controller.get_paginated_movies(page, view)

    return render_template("movies.html", paginated_movies=paginated_movies, view=view)


@app.route("/movies/filter_helper", methods=["POST"])
def movies_filter_helper():
    return redirect(url_for("movies_root", page=1, view=request.form["radio"]))


@app.route("/movies/search_helper", methods=["POST"])
def movies_search_helper():
    return redirect(url_for("movies_search", search=request.form["search_text"]))


@app.route("/movies/search=<search>")
@app.route("/movies/search=<search>/page=<page>")
def movies_search(page=1, search=None):

    page = int(page)
    m_controller = MovieController()
    paginated_movies = m_controller.get_paginated_movies_search(page, search)

    return render_template("movies.html", paginated_movies=paginated_movies)


@app.route("/movies/<movie>/")
def movies_instance(movie=None):

    m_controller = MovieController()
    movie = m_controller.get(movie)

    return render_template("movies_instance.html", movie=movie)


# ! Temporary, do not use in production
@app.route("/movies/populate")
def populate_mov():

    p = PopulateMovies()

    # p.print_names()
    p.populate_movies()

    return redirect("/movies/")


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
