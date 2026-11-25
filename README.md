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
