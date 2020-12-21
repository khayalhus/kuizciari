import psycopg2 as dbapi2

def connect(): # connects to db and returns cursor
    try: connection = dbapi2.connect(user="postgres",password="huseynov18",host="127.0.0.1",port="5432",database="postgres")
    except: print("Could not connect to database")
    return connection

connection = connect()
cursor = connection.cursor()

def get_courses():
    statement = """SELECT  "Class"."crn", "Class"."courseCode", "courseTitle", "instructorName", "Class"."semester"
                    FROM "Class"
                    LEFT JOIN "Course" ON "Class"."courseCode" = "Course"."courseCode"
                    LEFT JOIN "Instructs" ON 
                    "Instructs"."crn" = "Class"."crn"
                    AND "Instructs"."semester" = "Class"."semester"
                    LEFT JOIN "Instructor" ON
                    "Instructor"."instructorID" = "Instructs"."instructorID";"""
    cursor.execute(statement)
    courses = cursor.fetchall()
    return courses

def get_course(crn, semester):
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
    course = cursor.fetchone()
    return course