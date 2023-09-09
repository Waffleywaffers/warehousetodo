import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from datetime import datetime

from helpers import login_required

app = Flask(__name__)

db = SQL("sqlite:///whtd.db")

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

@app.route("/")
@login_required
def index():
    return render_template("base.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(user) != 1:
            return redirect("/login")
        
        session["user_id"] = user[0]["id"]
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        db.execute(
            "INSERT INTO users (username) VALUES(?)", username
        )
        return redirect("/login")
    else:
        return render_template("register.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/newtask", methods=["GET", "POST"])
@login_required
def newtask():
    if request.method == "POST":
        user_id = session["user_id"]
        task_name = request.form.get("task_name")
        reference = request.form.get("reference")
        task = request.form.get("task")
        now = datetime.now()
        datetime_string = now.strftime("%Y-%d-%m %H:%M:%S")
        print(user_id, task_name, reference, task, datetime_string)

        db.execute(
            "INSERT INTO tasks (user_id, task_name, reference, task, datetime) VALUES(?, ?, ?, ?, ?)",
            user_id,
            task_name,
            reference,
            task,
            datetime_string
        )

        return redirect("/")
    else:
        return render_template("newtask.html")