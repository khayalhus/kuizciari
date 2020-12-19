from flask import current_app, render_template, request, redirect, url_for, abort
from datetime import datetime
from database import connect, get_courses

today = datetime.today()
year_dec = today.strftime("%Y")

def home_page():
    return render_template("home.html", year = year_dec)

def courses_page():
    courses = get_courses()
    return render_template("courses.html", year = year_dec, courses = courses)