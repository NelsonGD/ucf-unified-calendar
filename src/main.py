from fastapi import FastAPI
import canvas_api

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return canvas_api.health()

@app.get("/courses")
async def courses_all():
    return canvas_api.list_courses()

@app.get("/courses/raw")
async def courses_raw():
    return canvas_api.raw_courses ()

@app.get("/courses/{course_id}/assignments")
async def course_assignments(course_id: int):
    return canvas_api.list_assignments(course_id)

@app.get("/all_assignments")
async def all_assignmets():
    return canvas_api.all_assignments()