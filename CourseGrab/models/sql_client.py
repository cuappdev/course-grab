import os
import pyodbc

class Client(object):
    def __init__(self):
        server = "tcp:coursegrabdb.database.windows.net"
        database = "coursegrabdb"   
        username = "nnsun"
        password = os.getenv("DB_PASSWORD")
        self.connection = pyodbc.connect("DRIVER={ODBC Driver 13 for SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s"
                            % (server, database, username, password))
        self.cursor = self.connection.cursor()


    def get_courses(self, id):
        print id
        command = "SELECT Subscription_1, Subscription_2, Subscription_3 FROM Users WHERE UserID = ?"
        self.cursor.execute(command, id)
        courses = self.cursor.fetchone()
        if courses is None:
            return []
        courses = [x for x in courses if x is not None]
        return courses


    def submit_request(self, id, email, course_num):
        command = "SELECT * FROM Courses WHERE CourseNum = ?"
        self.cursor.execute(command, course_num)
        row = self.cursor.fetchone()
        if row is None: 
            raise UserWarning("This course number does not exist.")

        command = "SELECT * FROM Users WHERE UserID = ? AND (Subscription_1 = ? OR Subscription_2 = ? OR Subscription_3 = ?)"
        self.cursor.execute(command, [id, course_num, course_num, course_num])
        if self.cursor.fetchone() is not None:
            raise UserWarning("You are already tracking this course.")

        command = "SELECT * FROM Users WHERE Email = ?"
        self.cursor.execute(command, email)
        row = self.cursor.fetchone()
        if row is None:
            command = "INSERT INTO Users (UserID, Email, Subscription_1, TrackStatus_1) VALUES (?, ?, ?, 1)"
            self.cursor.execute(command, [id, email, course_num])
        elif row.Subscription_1 is None:
            command = "UPDATE Users SET Subscription_1 = ?, TrackStatus_1 = 1"
            self.cursor.execute(command, course_num)
        elif row.Subscription_2 is None:
            command = "UPDATE Users SET Subscription_2 = ?, TrackStatus_2 = 1"
            self.cursor.execute(command, course_num)
        elif row.Subscription_3 is None:
            command = "UPDATE Users SET Subscription_3 = ?, TrackStatus_2 = 1"
            self.cursor.execute(command, course_num)
        else:
            raise UserWarning("You cannot track more than three courses at a time.")
        self.cursor.commit()


    def remove_course(self, id, course_num):
        command = "SELECT * FROM Users WHERE UserID = ?"
        self.cursor.execute(command, id)
        row = self.cursor.fetchone()
        if row.Subscription_1 == course_num:
            command = "UPDATE Users SET Subscription_1 = NULL"
            self.cursor.execute(command)
        elif row.Subscription_2 == course_num:
            command = "UPDATE Users SET Subscription_2 = NULL"
            self.cursor.execute(command)
        else:
            command = "UPDATE Users SET Subscription_3 = NULL"
            self.cursor.execute(command)
        self.cursor.commit()
