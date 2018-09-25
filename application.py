import os

from flask import Flask, session, request, render_template, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#Goodreads
GoodreadsKey ="6FmDrXrBHdMm22IUXa5Kw"


@app.route("/")
@login_required
def index():
    """Index page"""
    books = db.execute("SELECT * FROM books LIMIT 10;").fetchall()
    rating = []
    for book in books:
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GoodreadsKey, "isbns": book.isbn})
        # print(res.json()["books"][0]["average_rating"])
        rating.append(res.json()["books"][0]["average_rating"])
        # print(res.json())
        # print(res)
    return render_template("index.html", books=books, gr=rating)
    # return res
    # return "Project 1: TODO" + res


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    error = None

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            # return apology("must provide username", 403)
            flash("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")

        # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = :username",
        #                   username=request.form.get("username"))

        # Ensure username exists and password is correct
        # if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
        #     return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        # return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Missing username!")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("must provide password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("must provide password confirmation")

        # Ensure password and confirmation match
        elif not request.form.get("confirmation") == request.form.get("password"):
            flash("passwords does not match")

        # adduser = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
        #                      username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))
        # if not adduser:
        #     return apology("that username is taken", 400)
        # # generate_password_hash    db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)", username = request.form.get("username"), hash = hash)
        #
        # # Query database for username
        # rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        #
        # # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        # return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    return render_template("register.html")
    # return apology("TODO")

@app.route("/search")
def search():
    return "Search page"

@app.route("/api/<isbn>")
def api():
    return "API"