import json
from canvasapi import Canvas
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import date


load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
API_URL = os.getenv("CANVAS_API_URL", "https://webcourses.ucf.edu")
API_KEY = os.getenv("CANVAS_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing CANVAS_API_KEY. Create a .env file with CANVAS_API_KEY=... and ensure it's not committed.")

BASE = API_URL.rstrip("/")
canvas = Canvas(API_URL, API_KEY)

# Sanity check
def health():
    return {
        "ok" : True,
        "api_url": API_URL,
        "has_key": bool(API_KEY)
    }

# Display courses
def list_courses():
    return [
        {
            "courses_id": c.id,
            "name": c.name,
            "course_code": c.course_code,
        }
        for c in canvas.get_courses()
    ]


# Display Assignments
def list_assignments(course_id):
    course = canvas.get_course(course_id)

    return [
        {
            "course_id": course.id,
            "course_name": course.name,
            "assignment_id": a.id,
            "name": a.name,
            "due_at": a.due_at,
            "html_url": a.html_url
        }

        for a in course.get_assignments(order_by="due_at")
    ]

# Display raw data
def raw_courses():
    url = 'https://canvas.instructure.com'
    r = requests.get(url)
    return r.text


# Display all assignments
def all_assignments():
    assignments = []
    for c in canvas.get_courses():
        assignments.append(list_assignments(c.id))

    return assignments