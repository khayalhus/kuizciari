import psycopg2 as dbapi2

def connect(): # connects to db and returns cursor
    try: connection = dbapi2.connect(user="postgres",password="huseynov18",host="127.0.0.1",port="5432",database="postgres")
    except: print("Could not connect to database")
    return connection

def get_courses():
    connection = connect()
    cursor = connection.cursor()
    statement = """SELECT "courseCode", "courseTitle" FROM "Course" """
    cursor.execute(statement)
    courses = cursor.fetchall()
    return courses