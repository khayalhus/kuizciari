from flask import current_app, render_template, request, redirect, url_for, abort
from datetime import datetime
import json
import database

today = datetime.today()
year_dec = today.strftime("%Y")

def home_page():
    return render_template("home.html", year = year_dec)

def classes_page():
    if request.method == "GET":
        aclasses = database.get_classes()
        return render_template("classes.html", year = year_dec, aclasses = aclasses[0], instructors = aclasses[1], zip=zip)
    if request.method == "POST":
        keys = request.form.getlist("class_keys")
        for key in keys:
            loaded = json.loads(key)
            database.delete_class(loaded[0], loaded[1])
        return redirect(url_for("classes_page"))

def class_page(crn, semester):
    aclass = database.get_class(crn, semester)
    return render_template("class.html", year = year_dec, aclass = aclass)

'''
def course_addition_page():
    if request.method == "GET":
        values = {"crn": "", "semester": "", "courseCode": ""}
        return render_template(
            "class_edit.html",
            min_year=1887,
            max_year=datetime.now().year,
            values=values,
        )
    elif request.method == "POST":
        form_title = request.form["title"]
        form_year = request.form["year"]
        movie = Movie(form_title, year=int(form_year) if form_year else None)
        db = current_app.config["db"]
        movie_key = db.add_movie(movie)
        return redirect(url_for("movie_page", movie_key=movie_key))'''