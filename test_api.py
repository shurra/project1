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


res = db.execute("SELECT * FROM users;").fetchall()
create = db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, text TEXT NOT NULL, user_id INTEGER REFERENCES users, book_id INTEGER REFERENCES books)")

print(create)