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

def get_whole_class(crn, semester):
    statement = """SELECT "Class"."crn", "Class"."semester", "Class"."courseCode", "passGrade", "vfGrade", "quota", "enrolled"
                    FROM "Class"
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
    statement = """SELECT "Coursework"."workID", "CourseworkType"."workTitle", "Coursework"."startdate", "Coursework"."starttime", "Coursework"."enddate", "Coursework"."endtime", "Coursework"."grading", "Coursework"."workDescription"
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

def get_coursework(workID):
    statement = """SELECT "Coursework"."workID", "CourseworkType"."workTitle", "Coursework"."startdate", "Coursework"."starttime", "Coursework"."enddate", "Coursework"."endtime", "Coursework"."grading", "Coursework"."workDescription", "Coursework"."workType", "Coursework"."crn", "Coursework"."semester"
                    FROM "Coursework"
                    LEFT JOIN "CourseworkType" ON "CourseworkType"."workType" = "Coursework"."workType"
                    WHERE
                    "Coursework"."workID" = %(workID)s
                    ;
                """
    cursor.execute(statement, {'workID': workID})
    courseworks = cursor.fetchone()
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

def get_course(courseCode):
    statement = """SELECT "courseCode", "courseTitle", "courseDescription", "credits", "pool", "theoretical",  "tutorial", "laboratory", "necessity"
                    FROM "Course"
                    WHERE
                    "courseCode" = %(courseCode)s
                    ;
                """
    cursor.execute(statement, {'courseCode': courseCode})
    acourse = cursor.fetchone()
    return acourse

def update_course(courseCode, newCourseCode, courseTitle, description, credit, necessity, theoretical, tutorial, laboratory, pool):
    statement = """UPDATE "Course"
                    SET "courseCode" = %(newCourseCode)s,
                    "courseTitle" = %(courseTitle)s,
                    "courseDescription" = %(courseCode)s,
                    "credits" = %(credits)s,
                    "necessity" = %(necessity)s,
                    "theoretical" = %(theoretical)s,
                    "tutorial" = %(tutorial)s,
                    "laboratory" = %(laboratory)s,
                    "pool" = %(pool)s
                    WHERE "courseCode" = %(courseCode)s;
                    """
    try:
        cursor.execute(statement, {'courseCode': courseCode, 'newCourseCode': newCourseCode, 'courseTitle': courseTitle, 'courseDescription': description, 'credits': credit, 'necessity': necessity, 'theoretical': theoretical, 'tutorial': tutorial, 'laboratory': laboratory,'pool': pool})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def get_courses():
    statement = """SELECT "courseCode", "courseTitle" FROM "Course";"""
    cursor.execute(statement)
    courses = cursor.fetchall()
    return courses

def delete_course(courseCode):
    statement = """DELETE FROM "Course"
                    WHERE "courseCode" = %(courseCode)s;
                    """
    try:
        cursor.execute(statement, {'courseCode': courseCode})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def get_courseworkTypes():
    statement = """SELECT "workType", "workTitle" FROM "CourseworkType";"""
    cursor.execute(statement)
    courseworkTypes = cursor.fetchall()
    return courseworkTypes

def add_class(crn, semester, courseCode, passGrade, vfGrade, quota, enrolled):
    statement = """INSERT INTO "Class" ("crn", "semester", "courseCode", "passGrade", "vfGrade", "quota", "enrolled")
                    VALUES(%(crn)s, %(semester)s, %(courseCode)s, %(passGrade)s, %(vfGrade)s, %(quota)s, %(enrolled)s);"""
    try:
        cursor.execute(statement, {'crn': crn, 'semester': semester, 'courseCode': courseCode, 'passGrade': passGrade, 'vfGrade': vfGrade, 'quota': quota, 'enrolled': enrolled})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def update_class(crn, semester, newcrn, newsemester, courseCode, passGrade, vfGrade, quota, enrolled):
    statement = """UPDATE "Class"
                    SET "crn" = %(newcrn)s,
                    "semester" = %(newsemester)s,
                    "courseCode" = %(courseCode)s,
                    "passGrade" = %(passGrade)s,
                    "vfGrade" = %(vfGrade)s,
                    "quota" = %(quota)s,
                    "enrolled" = %(enrolled)s
                    WHERE "crn" = %(crn)s
                    AND
                    "semester" = %(semester)s
                    ;"""
    try:
        cursor.execute(statement, {'crn': crn, 'newcrn': newcrn, 'semester': semester, 'newsemester': newsemester, 'courseCode': courseCode, 'passGrade': passGrade, 'vfGrade': vfGrade, 'quota': quota, 'enrolled': enrolled})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_course(courseCode, courseTitle, description, credit, necessity, theoretical, tutorial, laboratory, pool):
    statement = """INSERT INTO "Course" ("courseCode", "courseTitle", "courseDescription", "credits", "necessity", "theoretical", "tutorial", "laboratory", "pool")
                    VALUES(%(courseCode)s, %(courseTitle)s, %(courseDescription)s, %(credits)s, %(necessity)s, %(theoretical)s, %(tutorial)s, %(laboratory)s, %(pool)s);"""
    try:
        cursor.execute(statement, {'courseCode': courseCode, 'courseTitle': courseTitle, 'courseDescription': description, 'credits': credit, 'necessity': necessity, 'theoretical': theoretical, 'tutorial': tutorial, 'laboratory': laboratory,'pool': pool})
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

def remove_instructs(crn, semester, instructorID):
    statement = """DELETE FROM "Instructs"
                    WHERE "crn" = %(crn)s
                    AND
                    "instructorID" = %(instructorID)s
                    AND "semester" = %(semester)s
                    ;
                    """
    try:
        cursor.execute(statement, {'instructorID': instructorID, 'crn': crn, 'semester': semester})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_courseworktype(workTitle, deadlineType):
    statement = """INSERT INTO "CourseworkType" ("workTitle", "deadlineType")
                    VALUES(%(workTitle)s, %(deadlineType)s);"""
    try:
        cursor.execute(statement, {'workTitle': workTitle, 'deadlineType': deadlineType})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def add_coursework(crn, semester, startdate, starttime, enddate, endtime, grading, description, workType):
    statement = """INSERT INTO "Coursework" ("crn", "semester", "startdate", "starttime", "enddate", "endtime", "grading", "workDescription", "workType")
                    VALUES(%(crn)s, %(semester)s, %(startdate)s, %(starttime)s, %(enddate)s, %(endtime)s, %(grading)s, %(description)s, %(workType)s);"""
    try:
        cursor.execute(statement, {'crn': crn, 'semester': semester, 'startdate': startdate, 'starttime': starttime, 'enddate': enddate, 'endtime': endtime, 'grading': grading, 'description': description, 'workType': workType})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def update_coursework(workID, startdate, starttime, enddate, endtime, grading, description, workType):
    statement = """UPDATE "Coursework"
                    SET "startdate" = %(startdate)s,
                    "starttime" = %(starttime)s,
                    "enddate" = %(enddate)s,
                    "endtime" = %(endtime)s,
                    "grading" = %(grading)s,
                    "workDescription" = %(description)s,
                    "workType" = %(workType)s
                    WHERE "workID" = %(workID)s
                    ;"""
    try:
        cursor.execute(statement, {'workID': workID, 'startdate': startdate, 'starttime': starttime, 'enddate': enddate, 'endtime': endtime, 'grading': grading, 'description': description, 'workType': workType})
        connection.commit()
        return True
    except dbapi2.DatabaseError:
        connection.rollback()
        return False

def delete_coursework(id):
    statement = """DELETE FROM "Coursework"
                    WHERE "workID" = %(id)s;
                    """
    try:
        cursor.execute(statement, {'id': id})
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
