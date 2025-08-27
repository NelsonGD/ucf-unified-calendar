import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from canvasapi import Canvas
import requests


app = FastAPI()


load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
API_URL = os.getenv("CANVAS_API_URL", "https://webcourses.ucf.edu")
API_KEY = os.getenv("CANVAS_API_KEY")

if not API_KEY:
    raise RuntimeError("Missing CANVAS_API_KEY. Create a .env file with CANVAS_API_KEY=... and ensure it's not committed.")

BASE = API_URL.rstrip("/")
canvas = Canvas(API_URL, API_KEY)

@app.get("/")
async def root():
    return {"message": "Hello World"}

# Sanity check
@app.get("/health")
async def health():
    return {
        "ok" : True,
        "api_url": API_URL,
        "has_key": bool(API_KEY)
    }

@app.get("/assignments")
async def get_assignments():
    user = canvas.get_current_user()
    courses = user.get_courses(enrollment_state='active')
    all_assignments = []
    for course in courses:
        try:
            assignments = course.get_assignments(order_by="due_at")
            for a in assignments:
                if a.due_at:  # Only show assignments with due dates
                    all_assignments.append({
                        "course": course.name,
                        "id": course.id,
                        "assignment": a.name,
                        "due_at": a.due_at,
                        "html_url": a.html_url
                    })
        except Exception as e:
            print(f"Error loading assignments for {course}: {e}")
    return all_assignments

@app.get("/courses")
async def list_courses():
    user = canvas.get_current_user()
    courses = user.get_courses(enrollment_state='active')
    return [
        {
            "id": c.id,
            "name": getattr(c, "name", None),
            "course_code": getattr(c, "course_code", None)
        }
        for c in courses
    ]

@app.get("/courses/completed")
async def list_completed_courses():
    """
    List courses where your enrollment is completed (i.e., past terms).
    """
    user = canvas.get_current_user()
    # Canvas supports filtering by enrollment_state='completed' and state=['completed']
    courses = user.get_courses(enrollment_state='completed', state=['completed'])
    return [
        {
            "id": c.id,
            "name": getattr(c, "name", None),
            "course_code": getattr(c, "course_code", None)
        }
        for c in courses
    ]

@app.get("/courses/all")
async def list_all_courses():
    """
    List active + completed courses (broad net). Useful when you're between terms.
    """
    user = canvas.get_current_user()
    # Pull both active and completed enrollments; include published/available and completed course states
    courses = user.get_courses(
        enrollment_state=['active', 'completed', 'invited_or_pending'],
        state=['available', 'completed', 'unpublished']
    )
    # De-duplicate by id while preserving first seen
    seen = set()
    out = []
    for c in courses:
        if c.id in seen:
            continue
        seen.add(c.id)
        out.append({
            "id": c.id,
            "name": getattr(c, "name", None),
            "course_code": getattr(c, "course_code", None)
        })
    return out

@app.get("/cop3503")
async def get_cs1():
    user = canvas.get_current_user()
    courses = user.get_courses(enrollment_state='active')

    target_id = 1481452
    cs_course = next((c for c in courses if c.id == target_id), None)

    if cs_course is None:
        return {"error": "Course not found"}

    assignments = cs_course.get_assignments(order_by="due_at")
    cs_assignments = []
    for a in assignments:
        try:
            if a.due_at:
                cs_assignments.append({
                    "assignment": a.name,
                    "due_at": a.due_at,
                    "html_url": a.html_url
                })
        except Exception as e:
            print(f"Error loading assignments for {cs_course}: {e}")
    return cs_assignments

@app.get("/courses/{course_id}/assignments")
async def get_course_assignments(course_id: int):
    # Works for completed courses as long as your token still has read access.
    user = canvas.get_current_user()
    courses = user.get_courses(
        enrollment_state=['active', 'completed', 'invited_or_pending'],
        state=['available', 'completed', 'unpublished']
    )
    course = next((c for c in courses if c.id == course_id), None)
    if course is None:
        return {"error": "Course not found"}
    assignments = course.get_assignments(order_by="due_at")
    out = []
    for a in assignments:
        try:
            if a.due_at:
                out.append({
                    "assignment": a.name,
                    "due_date": a.due_at,
                    "html_url": a.html_url
                })
        except Exception as e:
            print(f"Error loading assignments for {course}: {e}")
    return out

@app.get("/courses/raw")
async def raw_courses():
    r = requests.get(
        f"{BASE}/api/v1/courses",
        headers={"Authorization:" : f"Bearer {API_KEY}"}
        )

    link_header = r.headers.get("Link", "")
    next_url = None
    
    for part in link_header.split(","):
        if 'rel="next"' in part:
            # URL is wrapped in <>
            next_url = part.split(";")[0].strip("<> ")
            break
    print("Next page:", next_url)

    return {
        "status": r.status_code,
        "next": next_url,
        "headers": dict(r.headers),
        "body": r.json()
    }

def _next_link(link_header: str) -> str | None:
    if not link_header:
        return None
    for part in link_header.split(","):
        part = part.strip()
        if 'rel="next"' in part:
            url = part.split(";", 1)[0].strip()
            if url.startswith("<") and url.endswith(">"):
                url = url[1:-1]
            return url
    return None

@app.get("/courses/raw_all")
async def raw_courses_all(per_page: int = 25):
    url = f"{BASE}/api/v1/courses?per_page={per_page}"
    all_courses = []

    while url:
        r = requests.get(url, headers={"Authorization": f"Bearer {API_KEY}"})
        r.raise_for_status()
        all_courses.extend(r.json())
        url = _next_link(r.headers.get("Link", ""))

    # Make the output readable (minimal fields, de-duped)
    out = []
    seen = set()

    for c in all_courses:
        cid = c.get("id")
        if cid in seen:
            continue
        seen.add(cid)
        out.append({
            "id": cid,
            "name": c.get("name") or c.get("course_code"),
            "course_code": c.get("course_code")
        })

    print(f"[raw_all] collected {len(all_courses)} items across pages; returning {len(out)} unique courses")

    return out

@app.get("/courses/{course_id}/assignments/all")
async def organized_course(course_id: int):

    user = canvas.get_current_user()
    courses = user.get_courses(
        enrollment_state=['active', 'completed', 'invited_or_pending'],
        state=['available', 'completed', 'unpublished']
    )
    course = next((c for c in courses if c.id == course_id), None)
    if course is None:
        return {"error": "Course not found"}
    assignments = course.get_assignments(order_by="due_at")
    out = []
    for a in assignments:
        try:
            if a.due_at:
                out.append({
                    "name": a.name,
                    "due": a.due_at,
                    "url": a.html_url
                })
        except Exception as e:
            print(f"Error loading assignments for {course}: {e}")
    return out