import psycopg2 as dbapi2

def connect(): # connects to db and returns cursor
    try: connection = dbapi2.connect(user="postgres",password="huseynov18",host="127.0.0.1",port="5432",database="postgres")
    except: print("Could not connect to database")
    return connection

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
    statement = """SELECT "Class"."crn", "Class"."semester", "courseTitle"
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

def get_courses():
    statement = """SELECT "courseCode", "courseTitle" FROM "Course";"""
    cursor.execute(statement)
    courses = cursor.fetchall()
    return courses

def add_class(crn, semester, courseCode):
    statement = """INSERT INTO "Class" ("crn", "semester", "courseCode")
                    VALUES(%(crn)s, %(semester)s, %(courseCode)s);"""
    cursor.execute(statement, {'crn': crn, 'semester': semester, 'courseCode': courseCode})
    connection.commit()
    return

def add_course(courseCode, courseTitle):
    statement = """INSERT INTO "Course" ("courseCode", "courseTitle")
                    VALUES(%(courseCode)s, %(courseTitle)s);"""
    cursor.execute(statement, {'courseCode': courseCode, 'courseTitle': courseTitle})
    connection.commit()
    return

def add_instructor(instructorName):
    statement = """INSERT INTO "Instructor" ("instructorName")
                    VALUES(%(instructorName)s);"""
    cursor.execute(statement, {'instructorName': instructorName})
    connection.commit()
    return

def add_instructs(crn, semester, instructorID):
    statement = """INSERT INTO "Instructs" ("instructorID", "crn", "semester")
                    VALUES(%(instructorID)s, %(crn)s, %(semester)s);"""
    cursor.execute(statement, {'instructorID': instructorID, 'crn': crn, 'semester': semester})
    connection.commit()
    return