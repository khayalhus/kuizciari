from flask import current_app, render_template, request, redirect, url_for, abort
from datetime import datetime
from database import connect, get_courses, get_course

today = datetime.today()
year_dec = today.strftime("%Y")

def home_page():
    return render_template("home.html", year = year_dec)

def courses_page():
    courses = get_courses()
    return render_template("courses.html", year = year_dec, courses = courses)

def course_page(crn, semester):
    course = get_course(crn, semester)
    return render_template("course.html", year = year_dec, course = course)

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