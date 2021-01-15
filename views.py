from flask import current_app, render_template, request, redirect, url_for, abort, session, flash
from datetime import datetime
from string import ascii_letters
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
    if request.method == "GET":
        if session.get('logged_in') is not None:
            userID = session.get('userID')
            follows = database.get_follow(userID, crn, semester)
        else:
            follows = None
        aclass = database.get_class(crn, semester)
        courseworks = database.get_courseworks(crn, semester)
        return render_template("class.html", year = year_dec, aclass = aclass, courseworks = courseworks, follows = follows)
    elif request.method == "POST":
        return redirect(url_for("class_page", crn = crn, semester = semester))

def add_follow_redirector(crn, semester, follows):
    userID = session.get('userID')
    if userID is not None:
        if follows == "follow":
            if database.add_follow(userID, crn, semester) is True:
                flash("You are now following this class", "success")
            else:
                flash("Unable to follow this class", "danger")
        elif follows == "unfollow":
            if database.remove_follow(userID, crn, semester) is True:
                flash("You have unfollowed this class", "success")
            else:
                flash("Unable to unfollow this class", "danger")
    else:
        flash("You are not logged in", "danger")
    return redirect(url_for("class_page", crn = crn, semester = semester))

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
        if database.add_class(form_crn, form_semester, form_courseCode) is True:
            for form_instructorID in form_instructorIDs:
                if database.add_instructs(form_crn, form_semester, form_instructorID) is False:
                    flash("Instructor " + str(form_instructorID) + " is already assigned to this class.", "danger")
            flash("Class with CRN " + form_crn +  " has been added.", "success")
            return redirect(url_for("classes_page"))
        else:
            flash("Class already exists.", "danger")
            return redirect(url_for("class_addition_page"))

def coursework_addition_page(crn, semester):
    if request.method == "GET":
        courseworkTypes = database.get_courseworkTypes()
        aclass = database.get_class(crn, semester)
        instructors = database.get_class_instructors(crn, semester)
        return render_template("coursework_edit.html", year = year_dec, courseworkTypes = courseworkTypes, aclass = aclass, instructors = instructors)
    elif request.method == "POST":
        #form_crn = request.form["crn"]
        #form_semester = request.form["semester"]
        form_date = request.form["date"]
        form_time = request.form["time"]
        form_grading = request.form["grading"]
        form_workType = request.form["workType"]
        if database.add_coursework(crn, semester, form_date, form_time, form_grading, form_workType) is True:
            flash("Coursework has been added to class with CRN " + str(crn) + ".", "success")
            return redirect(url_for("class_page", crn = crn, semester = semester))
        else:
            flash("Could not add coursework to class with CRN" + str(crn) + ".", "danger")
            return redirect(url_for("coursework_addition_page", crn = crn, semester = semester))

def courseworktype_addition_page():
    if request.method == "GET":
        return render_template("courseworktype_edit.html", year = year_dec)
    elif request.method == "POST":
        form_workTitle = request.form["workTitle"]
        if database.add_courseworktype(form_workTitle) is False:
            flash("An unknown error occured when adding new coursework type.", "danger")
            return redirect(url_for("courseworktype_addition_page"))
        flash("Coursework type " + form_workTitle + " has been successfully added to the database.", "success")
        return redirect(url_for("classes_page"))

def course_addition_page():
    if request.method == "GET":
        values = {"facultyCode": "", "courseNumber": "", "language": "E", "courseTitle": "", "description": "", "credits": "", "compulsory": "", "elective": "", "theoretical": "", "tutorial": "", "laboratory": "", "pool": ""}
        return render_template("course_edit.html", year = year_dec, values = values)
    elif request.method == "POST":
        form_facultyCode = request.form["facultyCode"]
        form_courseNumber = request.form["courseNumber"]
        form_language = request.form["language"]
        form_courseTitle = request.form["courseTitle"]
        form_description = request.form["description"]
        form_credit = request.form["credits"]
        form_compulsory = request.form.get("compulsory")
        form_elective = request.form.get("elective")
        form_theoretical = request.form["theoretical"]
        form_tutorial = request.form["tutorial"]
        form_laboratory = request.form["laboratory"]
        form_pool = request.form["pool"]
        necessity = ""
        if form_compulsory is not None:
            necessity += form_compulsory
        if form_elective is not None:
            necessity += form_elective
        courseCode = "" + form_facultyCode + form_courseNumber + form_language
        if database.add_course(courseCode, form_courseTitle, form_description, form_credit, necessity, form_theoretical, form_tutorial, form_laboratory, form_pool) is False:
            flash("Course Code " + str(courseCode) + " already exists.", "danger")
            return redirect(url_for("course_addition_page"))
        flash("Course Code " + str(courseCode) + " has been successfully added.", "success")
        return redirect(url_for("class_addition_page"))

def instructor_addition_page():
    if request.method == "GET":
        return render_template("instructor_edit.html", year = year_dec)
    elif request.method == "POST":
        form_instructorName = request.form["instructorName"]
        if database.add_instructor(form_instructorName) is False:
            flash("An unknown error occured when adding new instructor.", "danger")
            return redirect(url_for("instructor_addition_page"))
        flash("Instructor " + form_instructorName + " has been successfully added to the database.", "success")
        return redirect(url_for("class_addition_page"))

def course_page(courseCode):
    if request.method == "GET":
        course = database.get_course(courseCode)
        if course is not None:
            return render_template("course.html", year = year_dec, course=course)
        else:
            flash("Course with code " + str(courseCode) + " could not be found.", "danger")
            return redirect(url_for("classes_page"))
    elif request.method == "POST":
        if database.delete_course(courseCode) is False:
            flash("An unknown error occured when removing course.", "danger")
            return redirect(url_for("course_page", courseCode=courseCode))
        flash("Course with code " + str(courseCode) + " and all related classes has been successfully removed from the database.", "success")
        return redirect(url_for("classes_page"))

def course_edit_page(courseCode):
    if request.method == "GET":
        raw_values = database.get_course(courseCode)
        if raw_values is None:
            flash("An unknown error occured when trying to open course for editing.", "danger")
            return redirect(url_for("classes_page"))
        else:
            #statement = """SELECT "courseCode", "courseTitle", "courseDescription", "credits", "pool", "theoretical",  "tutorial", "laboratory", "necessity"
            facultyCode = raw_values[0].rstrip("E").rstrip("0123456789")
            courseNumber = raw_values[0].lstrip(ascii_letters).rstrip("E")
            language = raw_values[0].lstrip(ascii_letters).lstrip("0123456789")
            compulsory = raw_values[8].strip("E")
            elective = raw_values[8].strip("C")
            mapped_values = {"facultyCode": facultyCode, "courseNumber": courseNumber, "language": language, "courseTitle": raw_values[1], "description": raw_values[2], "credits": raw_values[3], "compulsory": compulsory, "elective": elective, "theoretical": raw_values[5], "tutorial": raw_values[6], "laboratory": raw_values[7], "pool": raw_values[4]}
            return render_template("course_edit.html", year = year_dec, values = mapped_values)
    if request.method == "POST":
        form_facultyCode = request.form["facultyCode"]
        form_courseNumber = request.form["courseNumber"]
        form_language = request.form["language"]
        form_courseTitle = request.form["courseTitle"]
        form_description = request.form["description"]
        form_credit = request.form["credits"]
        form_compulsory = request.form.get("compulsory")
        form_elective = request.form.get("elective")
        form_theoretical = request.form["theoretical"]
        form_tutorial = request.form["tutorial"]
        form_laboratory = request.form["laboratory"]
        form_pool = request.form["pool"]
        necessity = ""
        if form_compulsory is not None:
            necessity += form_compulsory
        if form_elective is not None:
            necessity += form_elective
        newCourseCode = "" + form_facultyCode + form_courseNumber + form_language
        if database.update_course(courseCode, newCourseCode, form_courseTitle, form_description, form_credit, necessity, form_theoretical, form_tutorial, form_laboratory, form_pool) is False:
            flash("Could not update course " + str(courseCode) + " with the given values.", "danger")
            return redirect(url_for("course_edit_page", courseCode=courseCode))
        else:
            flash("Course " + str(courseCode) + " has been successfully updated.", "success")
            return redirect(url_for("course_page", courseCode=newCourseCode))

def login_page():
    if request.method == "GET":
        return render_template("login.html", year = year_dec)
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")
        exists = database.checkMail(email)
        if exists is True:
            matches = database.checkPass(email, password)
            if matches is None:
                flash("Incorrect password.", "danger")
                return redirect(url_for("login_page"))
            else:
                session['logged_in'] = True
                session['userID'] = matches[0]
                session['userType'] = matches[1]
                session['mail'] = email
                return redirect(url_for("profile_page"))
        else:
            flash("A user with this e-mail address does not exist.", "danger")
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
            flash("Account already exists.", "danger")
            return redirect(url_for("signup_page"))
        else:
            database.signup(email, password, userType)
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login_page"))

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