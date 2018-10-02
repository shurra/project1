import os

import re

from flask import Flask, session, request, render_template, flash, redirect, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

import requests

from helpers import login_required

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

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
    random_books = db.execute("SELECT * FROM books ORDER BY random() LIMIT 6;").fetchall()
    books = []
    img_pattern = r"<image_url>(.*?)</image_url>"
    for book in random_books:
        # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GoodreadsKey, "isbns": book.isbn})
        search_res = requests.get("https://www.goodreads.com/search/index.xml", params={"key": GoodreadsKey, "q": book.isbn}).text
        books.append(
            {"isbn": book.isbn,
             "title": book.title,
             "author": book.author,
             "rating": re.findall("<average_rating>(.*?)</average_rating>", search_res)[0],
             "img_url": re.findall("<image_url>(.*?)</image_url>", search_res)[0]}
        )
    return render_template("index.html", books=books)


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

        else:
            # Query database for user
            user = db.execute("SELECT * FROM users WHERE username = :username",
                              {"username": request.form.get("username")}).fetchone()
            # print(rows.id)
            # Ensure username exists and password is correct
            if not user or not check_password_hash(user.hash, request.form.get("password")):
                flash("invalid username and/or password")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = user.id
            session["user_name"] = user.username

            # Redirect user to home page
            return redirect("/search")

    # User reached route via GET (as by clicking a link or via redirect)
    # else:
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
        else:
            try:
                db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                           {"username": request.form.get("username"),
                            "hash": generate_password_hash(request.form.get("password"))})
                db.commit()
            except:
                flash("Username exist, or database error.")
                return redirect("/register")
        print("Username1 = ", request.form.get("username"))
        user_id = db.execute("SELECT id FROM users WHERE username = :username",
                             {"username": request.form.get("username")}).first()[0]
        # Login user
        session["user_id"] = user_id
        session["user_name"] = request.form.get("username")
        # Redirect user to search page
        return redirect("/search")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    # return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        books = db.execute("SELECT * FROM books WHERE isbn LIKE :query OR title ILIKE :query OR author ILIKE :query ORDER BY author",
                           {"query": "%" + request.form.get("query") + "%"}).fetchall()
        print("Query string = ", "%" + request.form.get("query") + "%")
        print("Search result = ", books)
        return render_template("search.html", books=books)

    return render_template("search.html")

@app.route("/book/<int:book_id>", methods=["GET", "POST"])
@login_required
def book_view(book_id):
    if request.method == "POST":
        if not request.form.get("rating") or request.form.get("review_text") == "":
            flash("Please leave rating and review text")
            return redirect("/book/" + str(book_id))
        # Checking existing user review for this book
        user_book_review = db.execute("SELECT COUNT(*) FROM reviews WHERE user_id=:user_id AND book_id=:book_id",
                                      {"user_id": session["user_id"], "book_id": book_id}).first()[0]
        if user_book_review > 0:
            flash("Only one review per book!")
            return redirect("/book/" + str(book_id))

        db.execute("INSERT INTO reviews (text, user_id, book_id, rating) VALUES (:review_text, :user_id, :book_id, :rating)",
                   {"review_text": request.form.get("review_text"), "user_id": session["user_id"], "book_id": book_id,
                    "rating": request.form.get("rating")})
        db.commit()
        return redirect("/book/" + str(book_id))
    book = infoBook(book_id)
    # print(book["reviews"][0][1])
    return render_template("book_view.html", book=book)

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if not book:
        abort(404)
    ratings = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": GoodreadsKey, "isbns": book.isbn}).json()
    return jsonify(title=book.title, author=book.author, year=book.year, isbn=book.isbn, review_count=ratings["books"][0]["reviews_count"], average_score=float(ratings["books"][0]["average_rating"]))

@app.route("/logout")
@login_required
def logout():
    # Forget any user_id
    session.clear()
    return redirect("/")

def infoBook(id):

    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()
    gr = requests.get("https://www.goodreads.com/book/review_counts.json",
                      params={"key": GoodreadsKey, "isbns": book.isbn}).json()
    xml_res = requests.get("https://www.goodreads.com/search/index.xml",
                           params={"key": GoodreadsKey, "q": book["isbn"]}).text
    # book_reviews = db.execute("SELECT * FROM reviews WHERE book_id=:id", {"id": id}).fetchall()
    book_reviews = db.execute("SELECT username, text, rating FROM users JOIN reviews ON reviews.user_id = users.id WHERE book_id=:book_id",
                              {"book_id": id}).fetchall()
    return {"isbn": book["isbn"],
            "id": book["id"],
            "author": book["author"],
            "title": book["title"],
            "year": int(book["year"]),
            "reviews_count": int(gr["books"][0]["reviews_count"]),
            "average_rating": float(gr["books"][0]["average_rating"]),
            "ratings_count": int(gr["books"][0]["ratings_count"]),
            "reviews": book_reviews,
            "img_url": re.findall("<image_url>(.*?)</image_url>", xml_res)[0]
            }