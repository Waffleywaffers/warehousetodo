from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime
import sqlite3
from helpers import login_required, check_null, apology, now, admin_required, my_file, get_admin_list

app = Flask(__name__)

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
    conn = sqlite3.connect(my_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    res = cur.execute(
        "SELECT * FROM tasks JOIN users ON id = user_id WHERE status = 'To do' ORDER BY datetime"
    )
    tasks = res.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", tasks=tasks)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    conn = sqlite3.connect(my_file)
    cur = conn.cursor()
    session.clear()
    if request.method == "POST":
        cur.execute(
            "SELECT * FROM users WHERE username =?", (request.form.get("username"),)
        )
        user = cur.fetchone() 
        if not user:
            return apology("Username not found") 
#Set session user_id  
        session["user_id"] = user[0]
        flash("Hi " + user[1] + "!")
        cur.close()
        conn.close()
#Set admin status to True if user_id is in the admin list
        for user in get_admin_list(my_file):
            if user["user_id"] == session["user_id"]:
                session["admin"] = True
            else:
                session["admin"] = False
        return redirect("/")
    else:
        return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
@admin_required
def register():
    conn = sqlite3.connect(my_file)
    cur = conn.cursor()
    if request.method == "POST":
# removing whitespeace and forcing lowercase
        username = (request.form.get("username")).strip().casefold()
# Some data validation 
        if not username:
            return apology("Please enter Username")

        try:
            cur.execute(
            "INSERT INTO users (username) VALUES(?)", (username,)
            )
        except sqlite3.IntegrityError:
            cur.close()
            conn.close()
            return apology("Username already exists")
        
        conn.commit()
        cur.close()
        conn.close()
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
            conn = sqlite3.connect(my_file)
            cur = conn.cursor()
            cur.execute(
            "INSERT INTO tasks (user_id, task_name, reference, task, datetime) VALUES(?, ?, ?, ?, ?)",
            (user_id,
            task_name,
            reference,
            task,
            datetime_string,)
            )
        except sqlite3.IntegrityError: 
            return apology("Please fill in all fields")
        
        conn.commit()
        cur.close()
        conn.close()
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
        task_name = check_null(request.form.get("task_name"))
        reference = check_null(request.form.get("reference"))
        task = check_null(request.form.get("task"))
        try:
            conn = sqlite3.connect(my_file)
            cur = conn.cursor()
            cur.execute(
                "UPDATE tasks SET task_name=?, reference=?, task=?, datetime=? WHERE task_id=?",(task_name, reference, task, datetime_string, task_id,)
            )
        except sqlite3.IntegrityError: 
            return apology("Please fill in all fields")          

        conn.commit()
        cur.close()
        conn.close()
        flash("Task Saved")
        return redirect("/")
# on GET request - prefill fields with task data
    else:
        conn = sqlite3.connect(my_file)
        cur = conn.cursor()
        
        task_id = request.args.get("task_id")
        cur.execute(
            "SELECT task_name, reference, task, task_id FROM tasks WHERE task_id = ?", (task_id,)
        )
        task_row = cur.fetchall()
        task_name = task_row[0][0]
        reference = task_row[0][1]
        task = task_row[0][2]
        task_id = task_row[0][3]

        cur.close()
        conn.close()

        return render_template("edittask.html", task_name=task_name, reference=reference, task=task, task_id=task_id)


# Delete Task with html modal for confirmation
@app.route("/deletetask", methods=["POST"])
@login_required
def deletetask():
    task_id = request.form.get("delete_task_id")
    conn = sqlite3.connect(my_file)
    cur = conn.cursor()
    cur.execute(
    "DELETE FROM tasks WHERE task_id = ?", (task_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Task " + task_id + " Deleted")
    return redirect("/")

    

# Complete task - update status of task    
@app.route("/completetask", methods=["POST", "GET"])
@login_required
def completetask():
    if request.method == "POST":
        task_id = request.form.get("task_id")
        date_time = now()
        conn = sqlite3.connect(my_file)
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET status = 'Completed', completed_datetime = ? WHERE task_id = ?", (date_time, task_id,) 
        )
        conn.commit()
        cur.close()
        conn.close()
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
        conn = sqlite3.connect(my_file)
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET status = 'To do', completed_datetime = ? WHERE task_id = ?", (None, task_id)
        )
        flash("Task " + task_id + " Status changed to To do")
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/")
    else:
        conn = sqlite3.connect(my_file)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()    
        cur.execute(
            "SELECT * FROM tasks JOIN users ON id = user_id WHERE status = 'Completed'"
        )
        completed_tasks = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("completed.html", completed_tasks=completed_tasks)
    
@app.route("/test", methods = ("POST", "GET"))
def test():
    if request.method == "POST":
        return redirect("/")
    else:
        return render_template("test.html")
