"""
This script runs the CourseGrab application using a development server.
"""

from os import environ
from src import app as application

if __name__ == '__main__':
    application.run(host='0.0.0.0')
