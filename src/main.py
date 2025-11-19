from fastapi import FastAPI
from . import canvas_api
from fastapi.responses import HTMLResponse

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
    return canvas_api.raw_courses()

@app.get("/courses/{course_id}/assignments")
async def course_assignments(course_id: int):
    return canvas_api.list_assignments(course_id)

@app.get("/all_assignments")
async def all_assignmets():
    return canvas_api.all_assignments()

@app.get("/assignments/present_future")
async def present_future():
    return canvas_api.present_and_future_assignments()

@app.get("/assignments/buckets")
async def buckets():
    return canvas_api.date_filter_all()

@app.get("/assignments/past")
async def past():
    return canvas_api.past_only_assignments()

# Pages with HTML #

# Present and Future assignments page with HTML
@app.get("/assignments/present_future.html", response_class=HTMLResponse)
async def present_future_html():
    items = canvas_api.present_and_future_assignments()
    if not items:
        return f"""
    
        <h1>Present & Future Assignments</h1>
        <br>
        No present or future items.

        """

    else:
        def row(a):
            course = a.get("course_name", "Unknown Course")
            name = a.get("name", "Untitled")
            due = a.get("due_at") or "No due date"
            link = a.get("html_url") or "#"
            return f"{course} - {name} - {due} - <a href=\"{link}\" target=\"_blank\" rel=\"noopener\">Open</a>"
        list_html = "<br>".join(row(a) for a in items) 
        total_assignments = len(items)
        return f"""
        
        <h1>Present & Future Assignments</h1>
        Total: {total_assignments}
        <br><br>
        {list_html}



        """
    
# Past assignments page with HTML
@app.get("/assignments/past.html", response_class=HTMLResponse)
async def past_html():
    items = canvas_api.past_only_assignments()
    if not items:
        return f"""
        
        <h1>Past Due Assignments:</h1>
        <br>
        No past due assignments
        
        """
    else:
        def row(a):
            name = a.get("name", "Untitled")
            course = a.get("course_name", "Unknown Course")
            due = a.get("due_at") or "No due date"
            link = a.get("html_url") or "#"
            return f"{course} - {name} - {due} - <a href=\"{link}\" target=\"_blank\" rel=\"noopener\">Open</a>"
        list_html = "<br>".join(row(a) for a in items)
        total_assignments = len(items)

        return f"""


        <h1>Past Assignments</h1>
        Total: {total_assignments}
        <br><br>
        {list_html}



        """

# Buckets page (All of the assignments) with HTML
@app.get("/assignments/buckets.html", response_class=HTMLResponse)
async def buckets_html():
    b = canvas_api.date_filter_all()
    def section(title, items):
        if not items:
                return f"{title}<br>No assignments in this time bracket"
        else:
            def row(a):
                name = a.get("name", "Untitled")
                course = a.get("course_name", "Unknown Course")
                due = a.get("due_at") or "No due date"
                link = a.get("html_url") or "#"

                return f"{course} - {name} - {due} - <a href=\"{link}\" target=\"_blank\" rel=\"noopener\">Open</a>"
            return f"{title}{'<br>'.join(row(a) for a in items)}"
    
    total_assignments = len(b["past"]) + len(b["present"]) + len(b["future"])
    return f"""



    <h1>P/D/F Assignments</h1>
    <h2>Total: {total_assignments}</h2>
    <h3>Past: {len(b['past'])} Present: {len(b['present'])} Future: {len(b['future'])}</h3>
    <br><br>
    {section("<h2>Past</h2>", b["past"])}
    {section("<h2>Present</h2>", b["present"])}
    {section("<h2>Future</h2>", b["future"])}



    """