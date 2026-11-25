import os
import sqlite3
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, jsonify, g
)

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or os.urandom(32)

# Database configuration
os.makedirs(app.instance_path, exist_ok=True)

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(app.instance_path, "management.db")
)


# Database connection
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


# Create database table
def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                course TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# Dashboard
@app.route("/")
def dashboard():
    db = get_db()

    total_students = db.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_courses = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    all_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "students.html",
        total_students=total_students,
        total_courses=total_courses,
        students=all_students
    )


# Student management page
@app.route("/students")
def students():
    db = get_db()

    all_students = db.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()
    total_courses = db.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]

    return render_template(
        "students.html",
        students=all_students,
        total_students=len(all_students),
        total_courses=total_courses
    )


# Add student
@app.route("/students/add", methods=["POST"])
def add_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    course = request.form.get("course", "").strip()

    if not name or not email or not course:
        flash("Please fill in all fields.", "error")
        return redirect(url_for("students"))

    if "@" not in email:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("students"))

    db = get_db()

    try:
        db.execute(
            """
            INSERT INTO students (name, email, course)
            VALUES (?, ?, ?)
            """,
            (name, email, course)
        )
        db.commit()

        flash("Student added successfully!", "success")

    except sqlite3.IntegrityError:
        flash("This email address is already registered.", "error")

    return redirect(url_for("students"))


# Delete student
@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    db = get_db()

    db.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )
    db.commit()

    flash("Student record deleted.", "success")

    return redirect(url_for("students"))


# JSON API
@app.route("/api/students", methods=["GET", "POST"])
def students_api():
    db = get_db()

    if request.method == "POST":
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "A JSON student record is required."}), 400

        name = data.get("name", "")
        email = data.get("email", "")
        course = data.get("course", "")

        if not all(isinstance(value, str) for value in (name, email, course)):
            return jsonify({"error": "Student fields must be text."}), 400

        name = name.strip()
        email = email.strip().lower()
        course = course.strip()

        if not name or not email or not course:
            return jsonify({"error": "Please fill in all fields."}), 400

        if "@" not in email:
            return jsonify({"error": "Please enter a valid email address."}), 400

        try:
            cursor = db.execute(
                """
                INSERT INTO students (name, email, course)
                VALUES (?, ?, ?)
                """,
                (name, email, course)
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify({
                "error": "This email address is already registered."
            }), 409

        student = db.execute(
            "SELECT id, name, email, course FROM students WHERE id = ?",
            (cursor.lastrowid,)
        ).fetchone()
        return jsonify(dict(student)), 201

    records = db.execute(
        "SELECT id, name, email, course FROM students ORDER BY id DESC"
    ).fetchall()

    return jsonify([
        dict(record) for record in records
    ])


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student_api(student_id):
    db = get_db()
    cursor = db.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({"error": "Student not found."}), 404

    return "", 204


# Health check
@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "MEVI Management Portal"
    })


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "5001"))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )