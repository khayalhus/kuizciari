import database

init_statements = [
"""
CREATE TABLE IF NOT EXISTS "User" (
  "userID" SERIAL,
  "mail" VARCHAR(255) NOT NULL UNIQUE,
  "password" BYTEA NOT NULL,
  "salt" BYTEA NOT NULL,
  "userType" VARCHAR(255) NOT NULL,
  PRIMARY KEY ("userID")
);""",
"""
CREATE TABLE IF NOT EXISTS "CourseworkType" (
  "workType" SERIAL,
  "workTitle" VARCHAR(255) NOT NULL,
  "deadlineType" VARCHAR(255) NOT NULL,
  PRIMARY KEY ("workType")
);""",
"""
CREATE TABLE IF NOT EXISTS "Instructor" (
  "instructorID" SERIAL,
  "instructorName" VARCHAR(255) NOT NULL,
  PRIMARY KEY ("instructorID")
);""",
"""
CREATE TABLE IF NOT EXISTS "Course" (
  "courseCode" VARCHAR(255) NOT NULL UNIQUE,
  "courseTitle" VARCHAR(255) NOT NULL,
  "courseDescription" VARCHAR(255),
  "credits" REAL NOT NULL,
  "pool" VARCHAR(255),
  "theoretical" INTEGER NOT NULL,
  "tutorial" INTEGER NOT NULL,
  "laboratory" INTEGER NOT NULL,
  "necessity" VARCHAR(255),
  PRIMARY KEY ("courseCode")
);""",
"""
CREATE TABLE IF NOT EXISTS "Class" (
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL, 
  "courseCode" VARCHAR(255) NOT NULL,
  "passGrade" INTEGER,
  "vfGrade" INTEGER,
  "quota" INTEGER,
  "enrolled" INTEGER,
  "syllabus" BYTEA,
  FOREIGN KEY ("courseCode") REFERENCES "Course" ("courseCode") ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY ("crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Instructs" (
  "instructorID" INTEGER NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  FOREIGN KEY ("instructorID") REFERENCES "Instructor" ("instructorID") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY ("instructorID", "crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Follows" (
  "userID" INTEGER NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  FOREIGN KEY ("userID") REFERENCES "User" ("userID") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY ("userID", "crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Coursework" (
  "workID" SERIAL NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  "startdate" DATE NOT NULL,
  "starttime" TIME NOT NULL,
  "enddate" DATE NOT NULL,
  "endtime" TIME NOT NULL,
  "grading" INTEGER NOT NULL,
  "workDescription" VARCHAR(255),
  "workType" INTEGER NOT NULL,
  FOREIGN KEY ("workType") REFERENCES "CourseworkType" ("workType") ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE ON UPDATE CASCADE,
  PRIMARY KEY ("workID")
);"""

]

def initialize():
    for statement in init_statements:
        database.cursor.execute(statement)
        database.connection.commit()
    return
  
if __name__ == "__main__":
  initialize()
