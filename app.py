import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime

from helpers import login_required, check_null, apology, now

app = Flask(__name__)

db = SQL("sqlite:///whtd2.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
# Homepage/dashboard
@app.route("/")
@login_required
def index():
# db.execute returns a dict (tasks) - which is passed to index.html via jinja syntax
    tasks = db.execute(
        "SELECT * FROM tasks JOIN users ON id = user_id WHERE status = 'To do' ORDER BY datetime"
    )
    return render_template("index.html", tasks=tasks)

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        print(user)
# If username not in dict (user) then return apology
        if len(user) != 1:
            return apology("Username not found")
# Setting session cookies        
        session["user_id"] = user[0]["id"]
        flash("Hi " + user[0]["username"] + "!")
        return redirect("/")
    else:
        return render_template("login.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
# removing whitespeace and forcing lowercase
        username = (request.form.get("username")).strip().casefold()
# Some data validation 
        if not username:
            return apology("Please enter Username")

        try:
            db.execute(
            "INSERT INTO users (username) VALUES(?)", username
            )
        except ValueError:
            return apology("Username already exists")
        
        return redirect("/login")
    else:
        return render_template("register.html")

# Logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# New task
@app.route("/newtask", methods=["GET", "POST"])
@login_required
def newtask():
    if request.method == "POST":
        user_id = session["user_id"]
        task_name = check_null(request.form.get("task_name"))
        reference = check_null(request.form.get("reference"))
        task = check_null(request.form.get("task"))
        now = datetime.now()
        datetime_string = now.strftime("%Y-%d-%m %H:%M:%S")
# Some data validation
        try:
            db.execute(
            "INSERT INTO tasks (user_id, task_name, reference, task, datetime) VALUES(?, ?, ?, ?, ?)",
            user_id,
            task_name,
            reference,
            task,
            datetime_string
            )
        except ValueError: 
            return apology("Please fill in all fields")
        
        flash("New Task Added")
        return redirect("/")
    else:
        return render_template("newtask.html")

# Edit existing task    
@app.route("/edittask", methods=["GET", "POST"])
@login_required
def edittask():
    if request.method == "POST":
        task_id = request.form.get("task_id")
        now = datetime.now()
        datetime_string = now.strftime("%Y-%d-%m %H:%M:%S")
        task_dict = {
                    "task_name": check_null(request.form.get("task_name")), 
                    "reference": check_null(request.form.get("reference")), 
                    "task": check_null(request.form.get("task"))
                    }

        edittask_row = db.execute(
            "SELECT task_name, reference, task FROM tasks WHERE task_id = ?", task_id
        )
        
        edittask_dict = edittask_row[0]

        for i in task_dict:
            if task_dict.get(i) != edittask_dict.get(i):
                try:
                    db.execute(
                        "UPDATE tasks SET ? = ? WHERE task_id = ?", i, task_dict.get(i), task_id
                    )
                except ValueError:
                    return apology("Please fill in all fields")          
        db.execute(
            "UPDATE tasks SET datetime = ? WHERE task_id = ?", datetime_string, task_id
        )
        flash("Task Saved")
        return redirect("/")
# on GET request - prefill fields with task data
    else:
        task_id = request.args.get("task_id")
        task_row = db.execute(
            "SELECT * FROM tasks WHERE task_id = ?", task_id
        )
        task_name = task_row[0]["task_name"]
        reference = task_row[0]["reference"]
        task = task_row[0]["task"]
        task_id = task_row[0]["task_id"]
        return render_template("edittask.html", task_name=task_name, reference=reference, task=task, task_id=task_id)

# Delete Task with html modal for confirmation
@app.route("/deletetask", methods=["POST", "GET"])
@login_required
def deletetask():
    if request.method == "POST":
        task_id = request.form.get("task_id")
        db.execute(
        "DELETE FROM tasks WHERE task_id = ?", task_id
        )
        flash("Task Deleted")
        return redirect("/")
    else:
        return redirect("/")
# Complete task - update status of task    
@app.route("/completetask", methods=["POST", "GET"])
@login_required
def completetask():
    if request.method == "POST":
        task_id = request.form.get("task_id")
        date_time = now()
        db.execute(
            "UPDATE tasks SET status = 'Completed', completed_datetime = ? WHERE task_id = ?", date_time, task_id, 
        )
        flash("Task " + task_id + " Complete!")
        return redirect("/")
    else:
        return redirect("/")
    
# Completed tasks page
@app.route("/completed", methods=["POST", "GET"])
@login_required
def completed():
    if request.method == "POST":
        task_id = request.form.get("task_id")
        db.execute(
            "UPDATE tasks SET status = 'To do', completed_datetime = ? WHERE task_id = ?", None, task_id
        )
        flash("Task " + task_id + " Status changed to To do")
        return redirect("/")
    else:    
        completed_tasks = db.execute(
            "SELECT * FROM tasks JOIN users ON id = user_id WHERE status = 'Completed'"
        )
        return render_template("completed.html", completed_tasks=completed_tasks)
