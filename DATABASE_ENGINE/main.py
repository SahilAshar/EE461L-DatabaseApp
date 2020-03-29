import datetime

from flask import Flask, redirect, render_template, url_for
from flask_mongoengine import MongoEngine

from controllers.about_controller import AboutController
from controllers.awards_controller import AwardController
from controllers.database_controller import initialize_db
from controllers.people_access_controller import PeopleAccessController
from controllers.years_controller import YearController

from populate_years import PopulateYears
from populate_people import PopulatePeople

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
@app.route("/years/page=<page>")
def year_root(page=1):

    page = int(page)
    y_controller = YearController()
    paginated_years = y_controller.get_paginated_years(page)

    return render_template("years.html", paginated_years=paginated_years)


@app.route("/years/<year>/")
def year_instance(year):

    y_controller = YearController()
    year_obj = y_controller.get(year)

    return render_template(
        "years_instance.html", year=year_obj.year, awards=year_obj.awards
    )


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
    y.populate()

    return redirect("/years/")


@app.route("/awards/")
def award_root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    return render_template("awards.html", awards=None)


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
def people_root(page=1):

    page = int(page)
    pa_controller = PeopleAccessController()
    paginated_people = pa_controller.get_paginated_people(page)

    return render_template("people.html", paginated_people=paginated_people)


@app.route("/people/<person>/")
def people_instance(person):

    # people = build_people.get_person_info(person)
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


@app.route("/movies/")
def movies_root():

    return render_template("movies.html", movie=None)


@app.route("/movies/<movie>/")
def movies_instance(movie):
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    return render_template("movies_instance.html", movie=None)


if __name__ == "__main__":
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host="127.0.0.1", port=8080, debug=True)
