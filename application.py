import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import requests

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


@app.route("/login")
def login():
    return "Login"

@app.route("/register")
def register():
    return "Register"

@app.route("/search")
def search():
    return "Search page"

@app.route("/api/<isbn>")
def api():
    return "API"