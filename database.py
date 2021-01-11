import psycopg2 as dbapi2
import hashlib
import os

url = os.getenv("DATABASE_URL")

if (url is None):
    url = "postgresql://postgres:huseynov18@127.0.0.1:5432/postgres"

def connect(): # connects to db and returns cursor
    try: conn = dbapi2.connect(url)
    except:
        conn = None
        print("Could not connect to database")
    return conn

connection = connect()
cursor = connection.cursor()

def get_classes():
    statement = """SELECT  "Class"."crn", "Class"."courseCode", "courseTitle", "Class"."semester"
                    FROM "Class"
                    LEFT JOIN "Course" ON "Class"."courseCode" = "Course"."courseCode";"""
    statement2 = """SELECT "instructorName" FROM "Instructs"
                    LEFT JOIN "Instructor" ON
                    "Instructor"."instructorID" = "Instructs"."instructorID"
                    WHERE
                    "Instructs"."crn" = %(crn)s
                    AND
                    "Instructs"."semester" = %(semester)s;
                    """
    cursor.execute(statement)
    temp = cursor.fetchall()
    i = 0
    instructors = []
    for crn, courseCode, courseTitle, semester in temp:
        instructors.append([])
        cursor.execute(statement2, {'crn': crn, 'semester': semester})
        instructors_query = cursor.fetchall()
        for instructor_info in instructors_query:
            instructors[i].append(instructor_info[0])
        i = i + 1
    classes = [temp, instructors]
    return classes

def get_class(crn, semester):
    statement = """SELECT "Class"."crn", "Class"."semester", "Class"."courseCode", "courseTitle"
                    FROM "Class"
                    LEFT JOIN "Course" ON "Class"."courseCode" = "Course"."courseCode"
                    WHERE
                    "Class"."crn" = %(crn)s
                    AND
                    "Class"."semester" = %(semester)s
                    ;
                """
    cursor.execute(statement, {'crn': crn, 'semester': semester})
    aclass = cursor.fetchone()
    return aclass

def get_courseworks(crn, semester):
    statement = """SELECT "Coursework"."workID", "Coursework"."date", "Coursework"."time", "Coursework"."grading", "CourseworkType"."workTitle"
                    FROM "Coursework"
                    LEFT JOIN "CourseworkType" ON "CourseworkType"."workType" = "Coursework"."workType"
                    LEFT JOIN "Class" ON "Class"."crn" = "Coursework"."crn" AND "Class"."semester" = "Coursework"."semester"
                    WHERE
                    "Class"."crn" = %(crn)s
                    AND
                    "Class"."semester" = %(semester)s
                    ;
                """
    cursor.execute(statement, {'crn': crn, 'semester': semester})
    courseworks = cursor.fetchall()
    return courseworks

def get_follow(userID, crn, semester):
    statement = """SELECT "Follows"."userID", "Follows"."crn", "Follows"."semester"
                    FROM "Follows"
                    WHERE
                    "Follows"."userID" = %(userID)s
                    AND
                    "Follows"."crn" = %(crn)s
                    AND
                    "Follows"."semester" = %(semester)s
                    ;
                """
    cursor.execute(statement, {'userID': userID, 'crn': crn, 'semester': semester})
    if cursor.fetchone() is not None:
        follows = True
    else:
        follows = False
    return follows

def delete_class(crn, semester):
    statement = """DELETE FROM "Class"
                    WHERE "crn" = %(crn)s
                    AND "semester" = %(semester)s
                    ;
                """
    cursor.execute(statement, {'crn': crn, 'semester': semester})
    connection.commit()
    return

def get_instructors():
    statement = """SELECT "instructorID", "instructorName" FROM "Instructor";"""
    cursor.execute(statement)
    instructors = cursor.fetchall()
    return instructors

def get_class_instructors(crn, semester):
    statement = """SELECT "Instructs"."instructorID", "instructorName" FROM "Instructs"
                LEFT JOIN "Instructor" ON "Instructor"."instructorID" = "Instructs"."instructorID"
                WHERE
                "Instructs"."crn" = %(crn)s
                AND
                "Instructs"."semester" = %(semester)s
                ;"""
    cursor.execute(statement, {'crn': crn, 'semester': semester})
    instructors = cursor.fetchall()
    return instructors

def get_courses():
    statement = """SELECT "courseCode", "courseTitle" FROM "Course";"""
    cursor.execute(statement)
    courses = cursor.fetchall()
    return courses
'''
def get_courseworks(crn, semester):
    statement = """SELECT "date", "time", "grading" "CourseworkType"."workTitle" FROM "Coursework"
                    WHERE
                    "Coursework"."crn" = %(crn)s
                    AND
                    "Coursework"."semester" = %(semester)s
                    LEFT JOIN "CourseworkType"
                    WHERE
                    "CourseworkType"."workType" = "Coursework"."workType"
                    ;"""
    cursor.execute(statement, {'crn': crn, 'semester': semester})
    courseworks = cursor.fetchall()
    return courseworks
'''
def get_courseworkTypes():
    statement = """SELECT "workType", "workTitle" FROM "CourseworkType";"""
    cursor.execute(statement)
    courseworkTypes = cursor.fetchall()
    return courseworkTypes

def add_class(crn, semester, courseCode):
    statement = """INSERT INTO "Class" ("crn", "semester", "courseCode")
                    VALUES(%(crn)s, %(semester)s, %(courseCode)s);"""
    try:
        cursor.execute(statement, {'crn': crn, 'semester': semester, 'courseCode': courseCode})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_course(courseCode, courseTitle):
    statement = """INSERT INTO "Course" ("courseCode", "courseTitle")
                    VALUES(%(courseCode)s, %(courseTitle)s);"""
    try:
        cursor.execute(statement, {'courseCode': courseCode, 'courseTitle': courseTitle})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_instructor(instructorName):
    statement = """INSERT INTO "Instructor" ("instructorName")
                    VALUES(%(instructorName)s);"""
    try:
        cursor.execute(statement, {'instructorName': instructorName})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_instructs(crn, semester, instructorID):
    statement = """INSERT INTO "Instructs" ("instructorID", "crn", "semester")
                    VALUES(%(instructorID)s, %(crn)s, %(semester)s);"""
    cursor.execute(statement, {'instructorID': instructorID, 'crn': crn, 'semester': semester})
    connection.commit()
    return

def add_courseworktype(workTitle):
    statement = """INSERT INTO "CourseworkType" ("workTitle")
                    VALUES(%(workTitle)s);"""
    try:
        cursor.execute(statement, {'workTitle': workTitle})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_coursework(crn, semester, date, time, grading, workType):
    statement = """INSERT INTO "Coursework" ("crn", "semester", "date", "time", "grading", "workType")
                    VALUES(%(crn)s, %(semester)s, %(date)s, %(time)s, %(grading)s, %(workType)s);"""
    try:
        cursor.execute(statement, {'crn': crn, 'semester': semester, 'date': date, 'time': time, 'grading': grading, 'workType': workType})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_follow(userID, crn, semester):
    statement = """INSERT INTO "Follows" ("userID", "crn", "semester")
                    VALUES(%(userID)s, %(crn)s, %(semester)s);"""
    try:
        cursor.execute(statement, {'userID': userID, 'crn': crn, 'semester': semester})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def remove_follow(userID, crn, semester):
    statement = """DELETE FROM "Follows"
                    WHERE "userID" = %(userID)s
                    AND
                    "crn" = %(crn)s
                    AND "semester" = %(semester)s
                    ;
                    """
    try:
        cursor.execute(statement, {'userID': userID, 'crn': crn, 'semester': semester})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False
                    
def signup(mail, password, userType):
    statement = """INSERT INTO "User" ("mail", "password", "salt", "userType")
                    VALUES(%(mail)s, %(password)s, %(salt)s, %(userType)s);"""
                    
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

    password_hashed = key + salt
    
    cursor.execute(statement, {'mail': mail, 'password': key, 'salt': salt, 'userType': userType})
    connection.commit()
    return

def checkMail(mail):
    statement = """SELECT "mail" FROM "User" WHERE
                    "User"."mail" = %(mail)s;"""
    cursor.execute(statement, {'mail': mail})
    out = cursor.fetchone()
    if out is None:
        return False
    else:
        return True

def checkPass(mail, password_attempt):
    statement1 = """SELECT "password", "salt" FROM "User" WHERE
                    "User"."mail" = %(mail)s;"""
                    
    cursor.execute(statement1, {'mail': mail})
    credentials = cursor.fetchone()

    salt = credentials[1]
    key = credentials[0]
    key_attempt = hashlib.pbkdf2_hmac('sha256', password_attempt.encode('utf-8'), salt, 100000)
    
    statement2 = """SELECT "userID", "userType" FROM "User" WHERE
                    "User"."mail" = %(mail)s
                    AND
                    "User"."password" = %(password)s;"""

    cursor.execute(statement2, {'mail': mail, 'password': key_attempt})
    userType = cursor.fetchone()
    return userType
