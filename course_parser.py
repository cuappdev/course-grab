import sys
import requests
import bs4
from src.models.db.sql_client import Client


"""
Parses the Cornell class roster and builds a SQL table of all courses
"""
def main():
    client = Client()

    # Delete old semester table, uncomment if creating new semester table
    # client.cursor.execute("DELETE FROM Courses")
    # client.cursor.commit()

    course_num_map = {}
    roster_page = "https://classes.cornell.edu"
    roster_request = requests.get(roster_page)
    roster_request.raise_for_status()
    split_url = roster_request.url.split('/')
    if split_url[-1] == '':
        semester = split_url[-2]
    else:
        semester = split_url[-1]
    print semester
    roster_bs4 = bs4.BeautifulSoup(roster_request.text, "html.parser")
    subject_tags = roster_bs4.select(".browse-subjectcode")

    subject_list = []
    for tag in subject_tags:
        subject_list.append(str(tag.getText()))

    subjects_page = "https://classes.cornell.edu/browse/roster/" + semester + "/subject/"
    # Section information is displayed as "Class Section ABC 123".
    # The offset enables grabbing only the relavent section information.
    section_offset = len("Class Section ")

    for subject_code in subject_list:
        print subject_code
        subject_request = requests.get(subjects_page + subject_code)
        subject_bs4 = bs4.BeautifulSoup(subject_request.text, "html.parser")
        course_code_tags = subject_bs4.find_all("strong", class_ = "tooltip-iws")
        for tag in course_code_tags:
            course_num = int(tag.getText().strip())
            command = "SELECT CourseNum FROM Courses WHERE CourseNum = ?"
            client.cursor.execute(command, course_num)
            if client.cursor.fetchone() is None:
                catalog_num = int("".join([x for x in tag.findNext("span", recursive=False)[0].getText() if x.isdigit()]))
                title = tag.parent.parent.parent.parent.parent.parent.parent.find_all("div", class_ = "title-coursedescr")[0].getText()
                section = str(tag.parent.parent.parent["aria-label"])[section_offset:]
                command = "INSERT INTO Courses (CourseNum, OpenStatus, SubjectCode, CatalogNum, Title, Section) VALUES (?, 0, ?, ?, ?, ?)"
                client.cursor.execute(command, [course_num, subject_code, catalog_num, title, section])
                print("    " + str(course_num))
    client.connection.commit()
    client.connection.close()

if __name__ == "__main__":
        main()
