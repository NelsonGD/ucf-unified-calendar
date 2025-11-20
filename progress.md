<file name=0 path=/Users/nelsondiaz/Downloads/ucf-unified-calendar/progress.md>Project Goal:
- Create a program that will link my google calendar account with my canvas account.
- Gather all the upcoming assignments.
- Display them in my calendar with the name, class, link, and due date. 

So far:
- I get it to display the information I want. Name, due date, link, and class name.

Next:
- Get it to show only assignments due at a certain time. I need to learn how to filter.
- Implemented: assignments_due_at_hour(hour) to filter by local hour; also fixed date bucketing (past/present/future) and sorting.
- Show different ways:
    - Past, present, and future assignments.
    - Past assignments.
    - Present and future assignments.

Learning:
~ import json
    - Allows for convertion of Python data and JSON text. Read or write JSON. 
    - NOT FOR CREATING DICTIONARIES.
    - Dictionary -> native Python data.

THIS IS A PYTHON DICTIONARY
* This is just a data container 
return {
    "ok": True,
    "api_url": API_URL
}

Everything after is just classic key and value. Pretty straight foward.

- Canvas often returns 'Z' (UTC). Make it explicit so fromisoformat accepts it.

- Convert to local timezone and return component.

- For "if" statements:
    - Every if statement must be followed by a indented block.
    - If you just want to skip a some data or content then just put continue or pass.
    - Continue is good if you just want to move to the next data.
    - Use continue to skip to the next iteration of the loop when condition is met.</file>

Implemented:
- assignments_due_at_hour(hour) to filter by local hour; also fixed date bucketing (past/present/future) and sorting.

When writing HTML:
- attribute="value"
ALWAYS:
    - Use quotes
    - Use double quotes (")

Quick run through code:
- _prase_due_date_local(due_at_str):
    - due_at_str -> "2025-11-20T23:59:00Z"
        - If given then .replace 'Z' with '+00:00'
        - Becomes "2025-11-20T23:59:00+00:00"
        - Proper ISO format with timezone
    - datetime.fromisoformat()
        - Gives datetime in UTC
    - dt.astimezone()
        - Conversts UTC time to local timezone.
    - .date()
        - Drops time, keeps only date part so (2025, 11, 20)
    - If anything breaks then returns None.
    BASICALLY: Turn this due_at string into the local calendar date. If wrong then use None.

- _sort_by_due
    - Takes list of assignments and return a new list sorted by due date. No due date then assignents goes to the end of the list.
    - True if there is no date, False if the is a date.
        - In sorting: False comes before true. So assignments with a date come first. Assignments with no date go last.
    - date.max if None.
        - So real dates are sorted from oldest -> newest.
        A: due_at = "2025-11-20T23:59:00Z" -> Key becomes: (False, 2025-11-20)
        B: due_at = "2025-11-15T23:59:00Z" -> Key becomes: (False, 2025-11-15)
        C: due_at = None -> Key becomes: (True, date.max)

        Final Order: B, A, C

Learning about OAuth:
- To Begin: 
    - Get OAuth 2.0 client credentials through Google API console.
        - Client requests access token from Google Authorization server. Extracts token from response. Sends token to Google API you want to access.
    - Make sure you know what kind of credentials are needeed. A JS App doesn't need a secret but a Web Server App does.
    - "score" -> Controls the set of resources and operations that an access token permits.
    - Best practice to requests scopes incrementally. When access is required.

- Installed app vs Web App
    - Web App & Installed App: 
        - Your app requests the token from the user which is given by login in and giving consent (done in the Google server).
        - Authorization code is given to the app.
        - App and Google servers exchange coke for token.
        - Token in the server gives a response.
        - Token is used by app to call Google API.

Google Calendar API Basics:
- What is a calendar?
    - Collection of events. Each one has metadata; Description or default calendar time zone. Represented by calendar source.
        - https://developers.google.com/workspace/calendar/v3/reference/calendars

- What is an event?
    - Contains information such as title, start and end times, and attendees. Can be single or recurring. Represented by an event source.
        -https://developers.google.com/workspace/calendar/api/v3/reference/events#resource-representations

- Event fields: https://developers.google.com/calendar/api/guides/overview

- start
    - NESTED OBJECT
        - INCLUSIVE start time of the event. Start of the first instance for recurring events.
    Fields:
    - "date": date
    - "dateTime": dateTime
    - "timezone": string


- end
    - NESTED OBJECT
        - EXCLUSIVE end time of event. End time of the first instance for recurring events.
    FIELDS:
    - "date": date
    - "dateTime": dateTime
    - "timezone": string

- summary
 - Takes a string.
 - TITLE OF THE EVENT

- description
    - Takes a string.
    - Description of the event. Can contain HTML (Optional).