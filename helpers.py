import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from datetime import datetime
import sqlite3
from pathlib import Path


from flask import redirect, render_template, session
from functools import wraps

THIS_FOLDER = Path(__file__).parent.resolve()
my_file = THIS_FOLDER / "whtd2.db"

conn = sqlite3.connect(my_file)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute(
    "SELECT * FROM admin"
)
admin_list = cur.fetchall()
cur.close()
conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def check_null(string):
    if not string:
        return None
    else:
        return string
    
def apology(message):
    return render_template("apology.html", message=message)

def now():
    now = datetime.now()
    return now.strftime("%Y-%d-%m %H:%M:%S")

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is False:
            return apology("Requires Admin Access")
        return f(*args, **kwargs)
    return decorated_function