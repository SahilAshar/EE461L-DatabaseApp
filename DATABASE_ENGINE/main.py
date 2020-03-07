import datetime

from flask import Flask, render_template
import build_awards
import build_people
import build_years
import build_about

app = Flask(__name__)


@app.route("/")
@app.route("/home")
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [
        datetime.datetime(2018, 1, 1, 10, 0, 0),
        datetime.datetime(2018, 1, 2, 10, 30, 0),
        datetime.datetime(2018, 1, 3, 11, 0, 0),
    ]

    return render_template("index.html")


@app.route("/about")
def about():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    issues_obj = build_about.return_issue_obj()
    commits_obj = build_about.return_commit_obj()

    return render_template("about.html", issues=issues_obj, commits=commits_obj)


@app.route("/years/")
def year_root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    return render_template("years.html", year=None)


@app.route("/years/<year>/")
def year_instance(year):

    year_dict = {"num": year}
    year_awards = build_years.get_year_info(year)
    # year_awards = year.awards

    return render_template("years_instance.html", year=year_dict, awards=year_awards)


@app.route("/awards/")
def award_root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.

    return render_template("awards.html", awards=None)


@app.route("/awards/<award>/")
def award_instance(award):

    if award == "actor-in-a-leading-role":
        awards = build_awards.get_best_actor_list()
    elif award == "actress-in-a-leading-role":
        awards = build_awards.get_best_actress_list()
    elif award == "directing":
        awards = build_awards.get_best_director_list()

    return render_template("awards_instance.html", awards=awards)


@app.route("/people/")
def people_root():

    return render_template("people.html", people=None)


@app.route("/people/<person>/")
def people_instance(person):

    people = build_people.get_person_info(person)

    return render_template("people_instance.html", people=people)


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
