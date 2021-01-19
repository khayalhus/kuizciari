from flask import current_app, render_template, request, redirect, url_for, abort, session, flash, send_file
from datetime import datetime
from string import ascii_letters
import json
import database
import sys
import os
import hashlib

import io


today = datetime.today()
year_dec = today.strftime("%Y")

def home_page():
    return render_template("home.html", year = year_dec)

def semesters_page():
    semesters = database.get_semesters()
    return render_template("semesters.html", year = year_dec, semesters = semesters)

def courses_page():
    if request.method == "GET":
        courses = database.get_courses()
        return render_template("courses.html", year = year_dec, courses = courses)
    elif request.method == "POST":
        if session.get('logged_in') is None:
            flash("You are not logged in", "danger")
            return redirect(url_for("login_page"))
        keys = request.form.getlist("course_keys")
        for key in keys:
            database.delete_course(key)
        return redirect(url_for("courses_page"))

def classes_page(semester):
    if request.method == "GET":
        aclasses = database.get_classes(semester)
        return render_template("classes.html", year = year_dec, aclasses = aclasses[0], instructors = aclasses[1], zip=zip)
    elif request.method == "POST":
        if session.get('logged_in') is None:
            flash("You are not logged in", "danger")
            return redirect(url_for("login_page"))
        keys = request.form.getlist("class_keys")
        for key in keys:
            loaded = json.loads(key)
            database.delete_class(loaded[0], loaded[1])
        return redirect(url_for("classes_page", semester=semester))

def class_page(crn, semester):
    if request.method == "GET":
        if session.get('logged_in') is not None:
            userID = session.get('userID')
            follows = database.get_follow(userID, crn, semester)
        else:
            follows = None
        aclass = database.get_whole_class(crn, semester)
        raw_courseworks = database.get_courseworks(crn, semester)
        mapped_courseworks = []
        for raw_coursework in raw_courseworks:
            mapped_courseworks.append({'id': raw_coursework[0], 'title': raw_coursework[1], 'startdate': raw_coursework[2], 'starttime': raw_coursework[3], 'enddate': raw_coursework[4], 'endtime': raw_coursework[5], 'grading': raw_coursework[6], 'description': raw_coursework[7]})
        return render_template("class.html", year = year_dec, aclass = aclass, courseworks = mapped_courseworks, follows = follows, zip=zip)
    elif request.method == "POST":
        if session.get('logged_in') is None:
            flash("You are not logged in", "danger")
            return redirect(url_for("login_page"))
        ids = request.form.getlist("class_keys")
        for workID in ids:
            if database.delete_coursework(workID) is False:
                flash("Something went wrong when deleting work with ID " + str(workID) + ".", "danger")
            else:
                flash("Successfully deleted work with ID " + str(workID) + ".", "success")
        return redirect(url_for("class_page", crn = crn, semester = semester))

def class_delete_redirector(crn, semester):
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if database.delete_class(crn, semester) is True:
        flash("Class with CRN " + str(crn) + " has been deleted.", "success")
        return redirect(url_for("classes_page", semester=semester))
    else:
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
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        values = {'crn': "", 'semester': "", 'courseCode': "", 'instructors': [], 'vfGrade': "", 'passGrade': "", 'quota': "", 'enrolled': "", 'syllabus': ""}
        instructors = database.get_instructors()
        courses = database.get_courses()
        return render_template("class_edit.html", year = year_dec, courses = courses, instructors = instructors, zip=zip, values = values)
    elif request.method == "POST":
        form_crn = request.form["crn"]
        form_semester = request.form["year"]
        form_semester += request.form["season"]
        form_courseCode = request.form["courseCode"]
        form_instructorIDs = request.form.getlist("instructors[]")
        form_passGrade = request.form["passGrade"]
        form_vfGrade = request.form["vfGrade"]
        form_quota = request.form["quota"]
        form_enrolled = request.form["enrolled"]
        form_syllabus = request.files['syllabus']
        if form_passGrade == "":
            form_passGrade = None
        if form_vfGrade == "":
            form_vfGrade = None
        if form_quota == "":
            form_quota = None
        if form_enrolled == "":
            form_enrolled = None
        filename = form_syllabus.filename
        file_ext = os.path.splitext(filename)[1]
        blob_data = None
        if(filename != ""):
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                flash("Syllabus file type can only be pdf", "danger")
                return redirect(url_for("class_addition_page"))
            else:
                blob_data = form_syllabus.read()
        if database.add_class(form_crn, form_semester, form_courseCode, form_passGrade, form_vfGrade, form_quota, form_enrolled, blob_data) is True:
            for form_instructorID in form_instructorIDs:
                if database.add_instructs(form_crn, form_semester, form_instructorID) is False:
                    flash("Instructor " + str(form_instructorID) + " is already assigned to this class.", "danger")
            flash("Class with CRN " + form_crn +  " has been added.", "success")
            return redirect(url_for("classes_page", semester=form_semester))
        else:
            flash("Class already exists.", "danger")
            return redirect(url_for("class_addition_page"))

def class_edit_page(crn, semester):
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        instructorIDs = []
        for instructor_info in database.get_class_instructors(crn, semester):
            instructorIDs.append(instructor_info[0])
        aclass = database.get_whole_class(crn, semester)
        instructors = database.get_instructors()
        courses = database.get_courses()
        mapped_values = {'crn': crn, 'semester': semester, 'courseCode': aclass[2], 'instructors': instructorIDs, 'vfGrade': aclass[5], 'passGrade': aclass[4], 'quota': aclass[6], 'enrolled': aclass[7], 'syllabus': ""}
        for key in mapped_values.keys():
            if mapped_values[key] is None:
                mapped_values[key] = ""
        return render_template("class_edit.html", year = year_dec, courses = courses, instructors = instructors, zip=zip, values = mapped_values)
    elif request.method == "POST":
        form_crn = request.form["crn"]
        form_semester = request.form["year"]
        print(form_semester)
        form_semester += request.form["season"]
        print(form_semester)
        form_courseCode = request.form["courseCode"]
        form_instructorIDs = request.form.getlist("instructors[]")
        form_passGrade = request.form["passGrade"]
        form_vfGrade = request.form["vfGrade"]
        form_quota = request.form["quota"]
        form_enrolled = request.form["enrolled"]
        form_syllabus = request.files['syllabus']
        if form_passGrade == "":
            form_passGrade = None
        if form_vfGrade == "":
            form_vfGrade = None
        if form_quota == "":
            form_quota = None
        if form_enrolled == "":
            form_enrolled = None
        instructorIDs = []
        for instructor_info in database.get_class_instructors(crn, semester):
            instructorIDs.append(instructor_info[0])
        filename = form_syllabus.filename
        file_ext = os.path.splitext(filename)[1]
        aclass = database.get_whole_class(crn, semester)
        blob_data = aclass[8]
        if(filename != ""):
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                flash("Syllabus file type can only be pdf", "danger")
                return redirect(url_for("class_edit_page", crn = crn, semester = semester))
            else:
                blob_data = form_syllabus.read()
        if database.update_class(crn, semester, form_crn, form_semester, form_courseCode, form_passGrade, form_vfGrade, form_quota, form_enrolled, blob_data) is True:
            for form_instructorID in form_instructorIDs:
                removed = False
                for instructorID in instructorIDs:
                    if form_instructorID == str(instructorID):
                        instructorIDs.remove(instructorID)
                        removed = True
                        break
                if removed is False:
                    if database.add_instructs(form_crn, form_semester, form_instructorID) is False:
                        flash("Instructor " + str(form_instructorID) + " is already assigned to this class.", "danger")
            for instructorID in instructorIDs:
                database.remove_instructs(form_crn, form_semester, instructorID)
            flash("Class with CRN " + form_crn +  " has been updated.", "success")
            return redirect(url_for("class_page", crn = form_crn, semester = form_semester))
        else:
            flash("Class with CRN " + str(crn) +  " could not be updated.", "danger")
            return redirect(url_for("class_edit_page", crn = crn, semester=semester))

def syllabus_page(crn, semester):
    aclass = database.get_whole_class(crn, semester)
    bytes_io = io.BytesIO(aclass[8])
    return send_file(bytes_io, mimetype='application/pdf')

def coursework_addition_page(crn, semester):
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        #def add_coursework(crn, semester, startdate, starttime, enddate, endtime, grading, description, workType):
        values = {'crn': "", 'semester': "", 'startdate': "", 'starttime': "", 'enddate': "", 'endtime': "", 'grading': "", 'description': "", 'workType': ""}
        courseworkTypes = database.get_courseworkTypes()
        aclass = database.get_class(crn, semester)
        instructors = database.get_class_instructors(crn, semester)
        return render_template("coursework_edit.html", year = year_dec, courseworkTypes = courseworkTypes, aclass = aclass, instructors = instructors, values=values)
    elif request.method == "POST":
        form_startdate = request.form["startdate"]
        form_starttime = request.form["starttime"]
        form_enddate = request.form["enddate"]
        form_endtime = request.form["endtime"]
        form_grading = request.form["grading"]
        form_workType = request.form["workType"]
        form_description = request.form["description"]

        if form_startdate > form_enddate:
            flash("Start date can not be later than end date", "danger")
            return redirect(url_for("coursework_addition_page", crn = crn, semester = semester))
        elif form_startdate == form_enddate:
            if form_starttime > form_endtime:
                flash("Start time can not be later than end time", "danger")
                return redirect(url_for("coursework_addition_page", crn = crn, semester = semester))

        if database.add_coursework(crn, semester, form_startdate, form_starttime, form_enddate, form_endtime, form_grading, form_description, form_workType) is True:
            flash("Coursework has been added to class with CRN " + str(crn) + ".", "success")
            return redirect(url_for("class_page", crn = crn, semester = semester))
        else:
            flash("Could not add coursework to class with CRN" + str(crn) + ".", "danger")
            return redirect(url_for("coursework_addition_page", crn = crn, semester = semester))

def coursework_page(workID):
    if request.method == "GET":
        coursework = database.get_coursework(workID)
        mapped_values = {'crn': coursework[9], 'semester': coursework[10], 'startdate': coursework[2], 'starttime': coursework[3], 'enddate': coursework[4], 'endtime': coursework[5], 'grading': coursework[6], 'description': coursework[7], 'workType': coursework[8], 'workID': coursework[0], 'workTitle': coursework[1]}
        aclass = database.get_class(mapped_values['crn'], mapped_values['semester'])
        return render_template("coursework.html", year = year_dec, aclass = aclass, values=mapped_values)
    elif request.method == "POST":
        if session.get('logged_in') is None:
            flash("You are not logged in", "danger")
            return redirect(url_for("login_page"))
        coursework = database.get_coursework(workID)
        mapped_values = {'crn': coursework[9], 'semester': coursework[10], 'startdate': coursework[2], 'starttime': coursework[3], 'enddate': coursework[4], 'endtime': coursework[5], 'grading': coursework[6], 'description': coursework[7], 'workType': coursework[8]}
        if database.delete_coursework(workID) is True:
            flash("Coursework with ID " + str(workID) + " has been deleted.", "success")
            return redirect(url_for("class_page", crn = mapped_values['crn'], semester = mapped_values['semester']))
        else:
            flash("Coursework with ID " + str(workID) + " could not be deleted.", "danger")
            return redirect(url_for("coursework_page", workID = workID))


def coursework_edit_page(workID):
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        coursework = database.get_coursework(workID)
        mapped_values = {'crn': coursework[9], 'semester': coursework[10], 'startdate': coursework[2], 'starttime': coursework[3], 'enddate': coursework[4], 'endtime': coursework[5], 'grading': coursework[6], 'description': coursework[7], 'workType': coursework[8]}
        courseworkTypes = database.get_courseworkTypes()
        aclass = database.get_class(mapped_values['crn'], mapped_values['semester'])
        instructors = database.get_class_instructors(mapped_values['crn'], mapped_values['semester'])
        return render_template("coursework_edit.html", year = year_dec, courseworkTypes = courseworkTypes, aclass = aclass, instructors = instructors, values=mapped_values)
    elif request.method == "POST":
        form_startdate = request.form["startdate"]
        form_starttime = request.form["starttime"]
        form_enddate = request.form["enddate"]
        form_endtime = request.form["endtime"]
        form_grading = request.form["grading"]
        form_workType = request.form["workType"]
        form_description = request.form["description"]

        if form_startdate > form_enddate:
            flash("Start date can not be later than end date", "danger")
            return redirect(url_for("coursework_page", workID = workID))
        elif form_startdate == form_enddate:
            if form_starttime > form_endtime:
                flash("Start time can not be later than end time", "danger")
                return redirect(url_for("coursework_page", workID = workID))
        
        if database.update_coursework(workID, form_startdate, form_starttime, form_enddate, form_endtime, form_grading, form_description, form_workType) is True:
            flash("Coursework with ID" + str(workID) + " has been updated.", "success")
            return redirect(url_for("coursework_page", workID=workID))
        else:
            flash("Coursework with ID" + str(workID) + " could not be updated.", "danger")
            return redirect(url_for("coursework_page", workID = workID))


def courseworktype_addition_page():
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        return render_template("courseworktype_edit.html", year = year_dec)
    elif request.method == "POST":
        form_workTitle = request.form["workTitle"]
        form_deadlineType = request.form["deadlineType"]
        if database.add_courseworktype(form_workTitle, form_deadlineType) is False:
            flash("An unknown error occured when adding new coursework type.", "danger")
            return redirect(url_for("courseworktype_addition_page"))
        flash("Coursework type " + form_workTitle + " has been successfully added to the database.", "success")
        return redirect(url_for("semesters_page"))

def course_addition_page():
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        values = {"facultyCode": "", "courseNumber": "", "language": "E", "courseTitle": "", "description": "", "credits": "", "compulsory": "", "elective": "", "theoretical": "", "tutorial": "", "laboratory": "", "pool": ""}
        return render_template("course_edit.html", year = year_dec, values = values)
    elif request.method == "POST":
        form_facultyCode = request.form["facultyCode"].upper()
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
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
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
            return redirect(url_for("courses_page"))
    elif request.method == "POST":
        if database.delete_course(courseCode) is False:
            flash("An unknown error occured when removing course.", "danger")
            return redirect(url_for("course_page", courseCode=courseCode))
        flash("Course with code " + str(courseCode) + " and all related classes has been successfully removed from the database.", "success")
        return redirect(url_for("courses_page"))

def course_edit_page(courseCode):
    if session.get('logged_in') is None:
        flash("You are not logged in", "danger")
        return redirect(url_for("login_page"))
    if request.method == "GET":
        raw_values = database.get_course(courseCode)
        if raw_values is None:
            flash("An unknown error occured when trying to open course for editing.", "danger")
            return redirect(url_for("courses_page"))
        else:
            facultyCode = raw_values[0].rstrip("E").rstrip("0123456789")
            courseNumber = raw_values[0].lstrip(ascii_letters).rstrip("E")
            language = raw_values[0].lstrip(ascii_letters).lstrip("0123456789")
            compulsory = raw_values[8].strip("E")
            elective = raw_values[8].strip("C")
            mapped_values = {"facultyCode": facultyCode, "courseNumber": courseNumber, "language": language, "courseTitle": raw_values[1], "description": raw_values[2], "credits": raw_values[3], "compulsory": compulsory, "elective": elective, "theoretical": raw_values[5], "tutorial": raw_values[6], "laboratory": raw_values[7], "pool": raw_values[4]}
            return render_template("course_edit.html", year = year_dec, values = mapped_values)
    if request.method == "POST":
        form_facultyCode = request.form["facultyCode"].upper()
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
                session['userID'] = matches
                session['mail'] = email
                return redirect(url_for("profile_works_page"))
        else:
            flash("A user with this e-mail address does not exist.", "danger")
            return redirect(url_for("login_page"))

def signup_page():
    if request.method == "GET":
        return render_template("signup.html", year = year_dec)
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        domain = email.split("@")[1]
        if domain != "itu.edu.tr":
            flash("Only ITU accounts are allowed", "danger")
            return redirect(url_for("signup_page"))
        isDuplicate = database.checkMail(email)
        if isDuplicate is True:
            flash("Account already exists.", "danger")
            return redirect(url_for("signup_page"))
        else:
            database.signup(email, password)
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login_page"))

def profile_works_page():
    if session.get('logged_in') is not None:
        courseworks = database.get_following_courseworks(session.get('userID'))
        mapped_values = []
        for coursework in courseworks:
            mapped_values.append({'workID': coursework[0], 'date': coursework[1], 'time': coursework[2], 'grading': coursework[3], 'crn': coursework[4], 'semester': coursework[5], 'courseCode': coursework[6], 'courseTitle': coursework[7], 'workTitle': coursework[8]})
        return render_template("profile_works.html", year = year_dec, courseworks = mapped_values, zip=zip)
    else:
        return redirect(url_for("login_page"))

def profile_follows_page():
    if session.get('logged_in') is not None:
        if request.method == "GET":
            aclasses = database.get_following_classes(session.get('userID'))
            mapped_values = []
            for aclass in aclasses[0]:
                mapped_values.append({'crn': aclass[0], 'courseCode': aclass[1], 'courseTitle': aclass[2], 'semester': aclass[3], 'passGrade': aclass[4], 'vfGrade': aclass[5], 'quota': aclass[6], 'enrolled': aclass[7], 'syllabus': aclass[8], 'count': aclass[9], 'sum': aclass[10]})
            return render_template("profile_follows.html", year = year_dec, aclasses = mapped_values, instructors = aclasses[1], zip=zip)
        if request.method == "POST":
            keys = request.form.getlist("class_keys")
            for key in keys:
                loaded = json.loads(key)
                database.remove_follow(session.get('userID'), loaded[0], loaded[1])
            return redirect(url_for("profile_follows_page"))
    else:
        return redirect(url_for("login_page"))

def logout_page():
    session.pop('logged_in', None)
    session.pop('userID', None)
    session.pop('mail', None)
    return redirect(url_for("login_page"))