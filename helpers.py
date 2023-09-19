import datetime
from datetime import datetime
import sqlite3
from pathlib import Path
from flask import redirect, render_template, session
from functools import wraps


#my_file variable to be the path of database
THIS_FOLDER = Path(__file__).parent.resolve()
my_file = THIS_FOLDER / "whtd2.db"

#query data base for a list of admin users
def get_admin_list(mydb):
    conn = sqlite3.connect(mydb)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM admin"
    )
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result


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

#return a stringified version of current datetime
def now():
    now = datetime.now()
    return now.strftime("%Y-%d-%m %H:%M:%S")

#restricts access to admin required functions
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("admin") is False:
            return apology("Requires Admin Access")
        return f(*args, **kwargs)
    return decorated_function