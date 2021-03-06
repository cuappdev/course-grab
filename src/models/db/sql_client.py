import datetime
from os import environ

import pyodbc
import pytz

class Client(object):

    DRIVER_CONNECT_STR = "DRIVER={ODBC Driver 17 for SQL Server};"

    def __init__(self):
        server = environ['DB_SERVER']
        database = environ['DB_NAME']
        username = environ['DB_USERNAME']
        password = environ['DB_PASSWORD']

        self.connection = pyodbc.connect(
            self.DRIVER_CONNECT_STR +
            "SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" % (server, database, username, password))
        self.cursor = self.connection.cursor()

    def add_user(self, id, email):
        est = pytz.timezone("America/New_York")
        time = pytz.utc.localize(datetime.datetime.now(), is_dst=None).astimezone(est)
        command = "SELECT * FROM Users WHERE UserID = ?"
        self.cursor.execute(command, id)
        if self.cursor.fetchone() is None:
            command = "INSERT INTO Users(UserID, Email, JoinedDatetime) VALUES (?, ?, ?)"
            self.cursor.execute(command, [id, email, time])
            self.cursor.commit()

    def get_courses(self, id):
        command = "SELECT C.CourseNum, Title, Section FROM Subscriptions S JOIN Courses C ON S.CourseNum = C.CourseNum WHERE UserID = ?"
        self.cursor.execute(command, id)
        course = self.cursor.fetchone()
        course_list = []
        while course is not None:
            course_list.append((course.CourseNum, course.Title, course.Section))
            course = self.cursor.fetchone()
        return course_list


    def submit_request(self, id, course_num):
        command = "SELECT * FROM Courses WHERE CourseNum = ?"
        self.cursor.execute(command, course_num)
        row = self.cursor.fetchone()
        if row is None:
            raise UserWarning("This course number is not in our database. It may take a bit for us to update our database with new courses added by the registrar.")

        command = "SELECT * FROM Subscriptions WHERE UserID = ? AND CourseNum = ?"
        self.cursor.execute(command, [id, course_num])
        if self.cursor.fetchone() is not None:
            raise UserWarning("You are already tracking this course.")

        command = "SELECT COUNT(*) as num_subs FROM Subscriptions WHERE UserID = ?"
        self.cursor.execute(command, id)
        row = self.cursor.fetchone()
        if row.num_subs == 3:
            raise UserWarning("You cannot track more than three courses at a time.")

        command = "INSERT INTO Subscriptions VALUES (?, ?, 1)"
        self.cursor.execute(command, [id, course_num])
        self.cursor.commit()


    def remove_course(self, id, course_num):
        command = "DELETE FROM Subscriptions WHERE UserID = ? AND CourseNum = ?"
        self.cursor.execute(command, [id, course_num])
        self.cursor.commit()

    def get_course_subject(self, course_num):
        command = "SELECT SubjectCode FROM Courses WHERE CourseNum = ?"
        self.cursor.execute(command, course_num)
        row = self.cursor.fetchone()
        if row is None:
            # course_num does not exist
            return None
        return row.SubjectCode
