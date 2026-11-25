# Student CRM

A lightweight student management app built with Flask, SQLite, and JavaScript.

## Features

- View student records and student/course totals
- Add students with name, email, and course
- Delete student records
- Store records in a local SQLite database

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5001/>.

The database is created at `instance/management.db` on first run. That local
database is intentionally excluded from version control.

For deployments, set the `SECRET_KEY` environment variable to a securely
generated value. If it is unset, the app generates a temporary development key
when it starts.

## Run with Docker

Build the image from the project directory:

```powershell
docker build --no-cache -t mevi-management:v1 .
```

Run it with a named volume so the SQLite database persists between containers:

```powershell
docker run --rm --name student-crm -p 5002:5001 -v student-crm-data:/app/instance mevi-management:v1
```

Open <http://127.0.0.1:5002/>. Port 5002 avoids conflicting with the local Flask
server if it is already running on port 5001. Set `SECRET_KEY` in the container
environment when deploying beyond local development.
