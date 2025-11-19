import json
from canvasapi import Canvas
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from datetime import date, datetime, timezone


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
            "course_id": c.id,
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
    assignments_all = []
    flat_list = []
    for c in canvas.get_courses():
        assignments_all.append(list_assignments(c.id))

    for class_a in assignments_all:
        for a in class_a:
            flat_list.append(a)

    return flat_list

# Adding date filtering to this shit
# Parse Canvas ISO8601 due_at into a local date
# (or None if missing/invalid).
def _parse_due_date_local(due_at_str):
    if not due_at_str:
        return None
    try: 
        dt = datetime.fromisoformat(due_at_str.replace('Z', '+00:00'))
        return dt.astimezone().date()
    except Exception:
        return None
    
# Return a new list sorted by due_at (None goes last)
def _sort_by_due(assignments):
    return sorted(
        assignments,
        key = lambda a:
        (_parse_due_date_local(a.get("due_at")) is None,
         _parse_due_date_local(a.get("due_at")) or date.max)
         )
# Adding date filtering
# Bucket all assignments into past/present/future,
# sorted by due date.
# Returns a dict: {"part": [...], "present": [...],
# "future": [...]}.
def date_filter_all():
    today = date.today()
    buckets = {"past": [], "present": [], "future": []}

    for a in all_assignments():
        d = _parse_due_date_local(a.get("due_at"))
        if d is None:
            # Skip undated items so buckets stay cool
            continue
        if d < today: 
            buckets["past"].append(a)
        elif d == today:
            buckets["present"].append(a)
        else:
            buckets["future"].append(a)

    # Sort each bucket by due date ascending
    for k in buckets:
        buckets[k] = _sort_by_due(buckets[k])
        
    return buckets

# Making it pretty or wtv
def past_only_assignments():
    """Only assignment strictly before today."""
    return date_filter_all()["past"]

def present_and_future_assignments():
    """Assignments due today or later."""
    b = date_filter_all()
    return b["present"] + b["future"]