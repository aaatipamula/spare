# Main Flask file
from datetime import datetime, timedelta
from flask import Flask, render_template, request, url_for, redirect, make_response
from database import Database
import os.path as path
from sqlite3 import IntegrityError
from email_testing import get_time, send_email

app = Flask("spare")
dbFile = path.join(__file__.replace('main.py', ''), 'database', 'database.db')
db = Database(dbFile)

@app.get("/")
def index():
    # rename the static files and stuff.
    return redirect(url_for('static', filename='index.html'))

@app.get("/user/feed")
def feed():
    community = request.args.get('community', '')
    # Make a converter for the different communities to display a nicer title.

    community = 'Daisy Hill'

    posts = db.select_all_posts()
    content = []

    for email, time, duration, item, post_type, tags in posts:
        name = db.select_one_user(email)[2]

        hour, minute, month, day, year = [int(x) for x in time.split('_')]
        _time = datetime(year, month, day, hour, minute) + timedelta(minutes=duration)
        time = _time.strftime("%l:%m %p %-m/%d/%Y")

        content.append((name, time, item, post_type, tags))

    return render_template('feed.html', content=content, community=community)

@app.get("/user/login")
def validateLogin():
    email = request.args.get('email', '')
    phone = request.args.get('phone_num', '')

    user = db.select_one_user(email)

    if user is None or not user[0] == phone:
        return render_template('retry_login.html', email=email, phone=phone), 401
    else:
        resp = make_response(redirect(url_for('feed', community=user[1])))
        resp.set_cookie('email', email)
        return resp

@app.get("/user/signup")
def validateSignup():
    email  = request.args.get('email',"")
    phone = request.args.get('phone_num',"")
    name = request.args.get('name',"")

    try:
        db.create_user((email,phone,0,'daisy_hill',name))
        resp = make_response(redirect(url_for('feed', community='daisy_hill')))
        resp.set_cookie('email', email)
        return resp

    except IntegrityError: 
        return render_template('retry_signup.html'), 404

@app.get("/posts/upload")
def uploadPost():
    items = request.args.get('items', '')
    duration = int(request.args.get('duration', ''))
    type_post = request.args.get('type', '')
    tags = request.args.get('tags', '')
    email = request.cookies.get('email')
    time = get_time()

    if email is None:
        return 404
    else:
        db.create_post((email, time, duration, items, type_post, tags))
        return redirect(url_for('feed', community='daisy_hill'))
