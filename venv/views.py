from flask import current_app, render_template, request, redirect, url_for, abort, session
from datetime import datetime
import json
import database
import sys
import os
import hashlib


today = datetime.today()
year_dec = today.strftime("%Y")

def home_page():
    return render_template("home.html", year = year_dec)

def classes_page():
    if request.method == "GET":
        aclasses = database.get_classes()
        return render_template("classes.html", year = year_dec, aclasses = aclasses[0], instructors = aclasses[1], zip=zip)
    elif request.method == "POST":
        keys = request.form.getlist("class_keys")
        for key in keys:
            loaded = json.loads(key)
            database.delete_class(loaded[0], loaded[1])
        return redirect(url_for("classes_page"))

def class_page(crn, semester):
    aclass = database.get_class(crn, semester)
    return render_template("class.html", year = year_dec, aclass = aclass)


def class_addition_page():
    if request.method == "GET":
        instructors = database.get_instructors()
        courses = database.get_courses()
        return render_template("class_edit.html", year = year_dec, courses = courses, instructors = instructors, zip=zip)
    elif request.method == "POST":
        form_crn = request.form["crn"]
        form_semester = request.form["semester"]
        form_courseCode = request.form["courseCode"]
        form_instructorIDs = request.form.getlist("instructors[]")
        database.add_class(form_crn, form_semester, form_courseCode)
        for form_instructorID in form_instructorIDs:
            database.add_instructs(form_crn, form_semester, form_instructorID)
        return redirect(url_for("classes_page"))

def course_addition_page():
    if request.method == "GET":
        return render_template("course_edit.html", year = year_dec)
    elif request.method == "POST":
        form_facultyCode = request.form["facultyCode"]
        form_courseNumber = request.form["courseNumber"]
        form_language = request.form["language"]
        form_courseTitle = request.form["courseTitle"]
        courseCode = "" + form_facultyCode + form_courseNumber + form_language
        database.add_course(courseCode, form_courseTitle)
        return redirect(url_for("class_addition_page"))

def instructor_addition_page():
    if request.method == "GET":
        return render_template("instructor_edit.html", year = year_dec)
    elif request.method == "POST":
        form_instructorName = request.form["instructorName"]
        database.add_instructor(form_instructorName)
        return redirect(url_for("class_addition_page"))

def login_page():
    if request.method == "GET":
        return render_template("login.html", year = year_dec)
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")
        exists = database.checkMail(email)
        matches = database.checkPass(email, password)
        if exists is True:
            if matches is None:
                return redirect(url_for("login_page"))
            else:
                session['logged_in'] = True
                session['userID'] = matches[0]
                session['userType'] = matches[1]
                session['mail'] = email
                return redirect(url_for("profile_page"))
        else:
            return redirect(url_for("login_page"))

def signup_page():
    if request.method == "GET":
        return render_template("signup.html", year = year_dec)
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        userType = request.form["userType"]
        isDuplicate = database.checkMail(email)
        if isDuplicate is True:
            return redirect(url_for("signup_page"))
        else:
            database.signup(email, password, userType)
            return redirect(url_for("profile_page"))

def profile_page():
    if session.get('logged_in') is not None:
        return render_template("profile.html", year = year_dec)
    else:
        return redirect(url_for("login_page"))

def logout_page():
    session.pop('logged_in', None)
    session.pop('userID', None)
    session.pop('userType', None)
    session.pop('mail', None)
    return redirect(url_for("login_page"))