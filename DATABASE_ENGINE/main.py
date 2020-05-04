from flask import Flask, abort, redirect, render_template, request, url_for

from controllers.database_controller import initialize_db

from controllers.about_controller import AboutController
from controllers.movies_controller import MoviesController
from controllers.people_controller import PeopleController
from controllers.ceremonies_controller import CeremoniesController

from populate.populate_movies import PopulateMovies
from populate.populate_people import PopulatePeople
from populate.populate_ceremonies import PopulateCeremonies

app = Flask(__name__)

app.config["DEBUG"] = True
app.config["MONGODB_SETTINGS"] = {
    "db": "omdb",
    "host": "mongodb+srv://sashar:qwerty12345@cluster0-0jhiw.gcp.mongodb.net/omdb?retryWrites=true&w=majority",
}

# Initializing DB separately, best practice for application factories
initialize_db(app)

# Initializing controllers separately, best practice for application factories
c_controller = CeremoniesController()
p_controller = PeopleController()
m_controller = MoviesController()


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


@app.route("/license")
def license():
    return render_template("license.html")


@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")


@app.errorhandler(500)
def page_not_found(error):
    return render_template("page_not_found.html", title="500"), 500


@app.route("/ceremonies/")
@app.route("/ceremonies/page=<page>/")
@app.route("/ceremonies/page=<page>/view=<view>")
def year_root(page=1, view="descending"):

    page = int(page)
    paginated_ceremonies = c_controller.get_paginated_years(page, view)

    return render_template(
        "years.html", paginated_years=paginated_ceremonies, view=view
    )


@app.route("/ceremonies/search_helper", methods=["POST"])
def year_search_helper():
    return redirect(url_for("year_search", search=request.form["search_text"]))


@app.route("/ceremonies/filter_helper", methods=["POST"])
def year_filter_helper():
    return redirect(url_for("year_root", page=1, view=request.form["radio"]))


@app.route("/ceremonies/search=<search>")
@app.route("/ceremonies/search=<search>/page=<page>")
def year_search(page=1, search=None):

    if search is None:
        redirect(url_for("year_search", search=request.form["search_text"]))

    page = int(page)
    paginated_years = c_controller.get_paginated_years_search(page, search)

    return render_template("years.html", paginated_years=paginated_years)


@app.route("/ceremonies/<ceremony_name>/")
def year_instance(ceremony_name=None):

    ceremony_obj = c_controller.get(ceremony_name)

    return render_template(
        "years_instance.html", year=ceremony_obj, awards=ceremony_obj.awards
    )


@app.route("/ceremonies/num/<year_num>/")
def ceremony_from_year_num(year_num=None):

    ceremony_name = c_controller.get_ceremony_name_by_year(year_num)

    return redirect(url_for("year_instance", ceremony_name=ceremony_name))

    # return render_template("years_instance.html", year=year_obj, awards=year_obj.awards)


# TODO : This works(?) Need to make this an actual post request
# ! Deprecated, left in here for legacy info. Endpoint is disabled.
# But this proves I can create actual controllers that can link
# @app.route("/ceremonies/new/<year>/")
def new_year(year):

    c_controller.post(year)

    return redirect("/ceremonies/" + year + "/")


# ! Used only for mass population.
# ! Endpoint is disabled in production!
# @app.route("/ceremonies/populate")
def populate_years():

    c = PopulateCeremonies()

    # c.get_wiki_image_link()
    # c.print_ordinal_numbers()
    # c.populate()
    # c.populate_wiki_images()
    # c.update_attributes()

    return redirect("/ceremonies/")


@app.route("/people/")
@app.route("/people/page=<page>")
@app.route("/people/page=<page>/view=<view>")
def people_root(page=1, view="ascending"):

    page = int(page)
    paginated_people = p_controller.get_paginated_people(page, view)

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

    page = int(page)
    paginated_people = pa_controller.get_paginated_people_search(page, search)

    return render_template("people.html", paginated_people=paginated_people)


@app.route("/people/<person>/")
def people_instance(person=None):

    people = pa_controller.get(person)

    if people is False:
        abort(500)

    return render_template("people_instance.html", people=people[0])


# TODO : This works(?) Need to make this an actual post request
# ! Deprecated, left in here for legacy info. Endpoint is disabled.
# But this proves I can create actual controllers that can link
# @app.route("/people/new/<person>/")
def new_person(person):

    pa_controller.post(person)

    return redirect("/people/" + person + "/")


# ! Used only for mass population.
# ! Endpoint is disabled in production!
# @app.route("/people/populate")
def populate_people():

    p = PopulatePeople()

    # p.print_names()
    # p.populate()
    # p.delete()
    # p.update_attributes()

    return redirect("/people/")


@app.route("/movies/")
@app.route("/movies/page=<page>")
@app.route("/movies/page=<page>/view=<view>")
def movies_root(page=1, view="ascending"):

    page = int(page)
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
    paginated_movies = m_controller.get_paginated_movies_search(page, search)

    return render_template("movies.html", paginated_movies=paginated_movies)


@app.route("/movies/<movie>/")
def movies_instance(movie=None):

    movie = m_controller.get(movie)

    if movie is False:
        abort(500)

    movie_year = movie.year.split(", ")[-1]

    return render_template("movies_instance.html", movie=movie, movie_year=movie_year)


# ! Used only for mass population.
# ! Endpoint is disabled in production!
def populate_movies():

    p = PopulateMovies()

    # p.print_names()
    # p.populate_movies()
    p.update_attributes()

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
