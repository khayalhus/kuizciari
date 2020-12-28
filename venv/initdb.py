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
  PRIMARY KEY ("courseCode")
);""",
"""
CREATE TABLE IF NOT EXISTS "Class" (
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL, 
  "courseCode" VARCHAR(255) NOT NULL,
  FOREIGN KEY ("courseCode") REFERENCES "Course" ("courseCode"),
  PRIMARY KEY ("crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Instructs" (
  "instructorID" INTEGER NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  FOREIGN KEY ("instructorID") REFERENCES "Instructor" ("instructorID"),
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE,
  PRIMARY KEY ("instructorID", "crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Follows" (
  "userID" INTEGER NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  FOREIGN KEY ("userID") REFERENCES "User" ("userID"),
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE,
  PRIMARY KEY ("userID", "crn", "semester")
);""",
"""
CREATE TABLE IF NOT EXISTS "Coursework" (
  "workID" SERIAL NOT NULL,
  "crn" INTEGER NOT NULL,
  "semester" INTEGER NOT NULL,
  "date" DATE,
  "grading" INTEGER NOT NULL,
  "workType" INTEGER NOT NULL,
  FOREIGN KEY ("workType") REFERENCES "CourseworkType" ("workType"),
  FOREIGN KEY ("crn", "semester") REFERENCES "Class" ("crn", "semester") ON DELETE CASCADE,
  PRIMARY KEY ("workID")
);"""

]

def initialize():
    for statement in init_statements:
        database.cursor.execute(statement)
        database.connection.commit()
    return