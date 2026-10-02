from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

# Secret key for login session
app.secret_key = "student-management-secret-key"


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CREATE TABLE
# =========================

def create_table():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            course TEXT NOT NULL,
            roll_no TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Admin login details
        if username == "admin" and password == "1234":

            session["logged_in"] = True

            return redirect("/")

        else:

            return render_template(
                "login.html",
                error="Invalid username or password"
            )

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("logged_in", None)

    return redirect("/login")


# =========================
# LOGIN CHECK
# =========================

def is_logged_in():

    return session.get("logged_in") == True


# =========================
# DASHBOARD
# =========================

@app.route("/")
def home():

    if not is_logged_in():
        return redirect("/login")

    search = request.args.get("search", "")

    conn = get_db()

    if search:

        students = conn.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ?
            OR roll_no LIKE ?
            OR course LIKE ?
            """,
            (
                "%" + search + "%",
                "%" + search + "%",
                "%" + search + "%"
            )
        ).fetchall()

    else:

        students = conn.execute(
            "SELECT * FROM students"
        ).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        students=students,
        total_students=total_students,
        search=search
    )


# =========================
# ADD STUDENT
# =========================

@app.route("/add", methods=["POST"])
def add_student():

    if not is_logged_in():
        return redirect("/login")

    name = request.form["name"]
    age = request.form["age"]
    course = request.form["course"]
    roll_no = request.form["roll_no"]

    conn = get_db()

    conn.execute(
        """
        INSERT INTO students (name, age, course, roll_no)
        VALUES (?, ?, ?, ?)
        """,
        (name, age, course, roll_no)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# VIEW STUDENT
# =========================

@app.route("/student/<int:id>")
def student_details(id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "student_details.html",
        student=student
    )


# =========================
# EDIT STUDENT
# =========================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        course = request.form["course"]
        roll_no = request.form["roll_no"]

        conn.execute(
            """
            UPDATE students
            SET name = ?, age = ?, course = ?, roll_no = ?
            WHERE id = ?
            """,
            (name, age, course, roll_no, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "edit.html",
        student=student
    )


# =========================
# DELETE STUDENT
# =========================

@app.route("/delete/<int:id>")
def delete_student(id):

    if not is_logged_in():
        return redirect("/login")

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    create_table()

app.run(debug=True)