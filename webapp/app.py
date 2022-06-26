#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for
import os
import flask_login
from passlib.hash import pbkdf2_sha256
from questions import get_animal_question_mc
import hashlib
from rating import get_new_ratings
from db import User, create_user, get_all_users
from time import time
from random import randrange
from requests import get
from json import loads

os.system(os.environ.get("COCKROACH_SSL_CMD"))

app = Flask(__name__)
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.secret_key = os.environ.get("SECRET_KEY")
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
species_data = loads(get('https://ecos.fws.gov/ecp/pullreports/catalog/species/report/species/export?format=json&columns=%2Fspecies%40cn%2Csn%2Cstatus%2Cdesc%2Cgn%3B%2Fspecies%2FspeciesImage%40image_url%2Cimage_citation&sort=%2Fspecies%40cn%20asc%3B%2Fspecies%40sn%20asc').text)['data']

class current_user_class(flask_login.UserMixin):
    pass

all_users, t = get_all_users(), time()

@login_manager.user_loader
def user_loader(id):
    user = User(id)
    assert user.id != -1, "Bad user passed to user_loader()"
    current_user = current_user_class()
    current_user.id = user.id
    current_user.username = user.username
    return current_user


@login_manager.request_loader
def request_loader(request):
    users = get_all_users()
    username = request.form.get('username')
    if username:
        username = username.lower()
    listofusernames = [user.username for user in users]
    if username not in listofusernames:
        return

    current_user = current_user_class()
    
    for user in users:
        if user.username == username:
            current_user.id = user.id
    
    return current_user

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return redirect(url_for("home"))
    username = request.form["username"].lower()
    user = User(username=username)
    if user.id == -1: 
        return redirect(url_for("home") + '?error=True&msg=Incorrect%20username%20or%20password.&username=' + request.form['username'])
    if pbkdf2_sha256.verify(request.form["password"], user.password) == True:
        flask_user = current_user_class()
        flask_user.id = user.id
        flask_login.login_user(flask_user)
        return redirect(url_for("home"))
    else:
        return redirect(url_for("home") + '?error=True&msg=Incorrect%20username%20or%20password.&username=' + request.form['username'])

@app.route("/register", methods=["POST"])
def register():
    if request.method == "GET":
        return redirect(url_for("home"))
    users = [user.username for user in get_all_users()]
    username = request.form["username"]
    password = pbkdf2_sha256.hash(request.form["password"])
    if username in users:
        return redirect(url_for("home") + '?error=True&msg=Username%20already%20taken.&username=' + request.form['username'])
    user = create_user(username, password)
    flask_user = current_user_class()
    flask_user.id = user.id
    flask_login.login_user(flask_user)
    # return """
    # Successfully registered
    # <script>setTimeout("window.location.replace('/?registered=True')", 2000);</script>
    # """
    return redirect(url_for("home"))



@app.route("/scroll_ep", methods=['GET'])
def scroll_ep():
    return str(species_data[randrange(0, len(species_data))])

@app.route("/")
def home():
    '''
    this should be the home page, with links to:
    login/register
    leaderboard of rating
    info/about
    play
    '''
    return render_template("index.html", x=request.args.get('registered'))

@app.route("/leaderboard")
def leaderboard():
    '''
    list all players from highest to lowest rating
    '''
    users = []
    all_users = get_all_users()
    for user in all_users:
        users.append([user.username, int(user.rating)])    
    users.sort(key=lambda x: x[1], reverse=True)
    return render_template("leaderboard.html", users=users)
	
@app.route("/play")
def play():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for("home") + "?login=True")
    
    return render_template('play.html', x=flask_login.current_user)

@app.route('/profile')
def profile():
    try:
        usrname = request.args.get('user')
	all_users = get_all_users()
        for user in all_users:
            print(user.username)
            if user.username == usrname:
                x = user
        return render_template('profile.html', x = x, md5username=hashlib.md5(x.username.encode()).hexdigest(), usrname=usrname)
    except:
        return """Sorry, this user either doesn't exist, or has not been loaded yet. Please wait 5-10 minutes before trying again.
        <script>setTimeout("window.location.replace('/')", 3000);</script>
        """

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return redirect(url_for("home"))
@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

app.run('0.0.0.0', 8080)

