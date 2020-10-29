import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from flask import jsonify
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///words.db")




@app.route("/")
def index():
   return render_template('index.html')

@app.route("/word")
def word():

    word = db.execute(" SELECT * FROM WORDS ORDER BY RANDOM() ")
    while ' ' in word [0] ['German']:
        word = db.execute(" SELECT * FROM WORDS ORDER BY RANDOM() ")
    word_details = { 'english': word [0] ['English'], 'german' : (word [0] ['German']).lower() }
    return jsonify (word_details)


@app.route("/submit", methods=['GET', 'POST'])
def submit():
    print('a')
    if request.method == "POST":
        print('b')
        name = request.form.get("name")
        score = int(request.form.get("score"))
        print(name)
        db.execute(" INSERT INTO 'score' ('name', 'score') VALUES (:name, :score)", name =  name, score = score)

        return redirect("/score")
    else:
        return redirect("/score")


@app.route("/score")
def score():

    rows = db.execute(" SELECT * FROM score ORDER BY Score desc")

    return render_template("score.html", rows = rows)

