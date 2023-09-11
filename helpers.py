import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from datetime import datetime

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
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