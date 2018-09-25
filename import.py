import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# postgres://reyktcizwqfkeh:3b566486c76c032b255767d78d00f7bc289ccc93283826f465c3825d8f1eff14@ec2-54-247-101-205.eu-west-1.compute.amazonaws.com:5432/ddgv5q820v7o4r

# Database object
engine = create_engine(os.getenv("DATABASE_URL"), echo=False)
db = scoped_session(sessionmaker(bind=engine))


def main():
    """Main function"""
    # Creating table for books in db
    db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR(13) NOT NULL, title VARCHAR(50) NOT NULL, author VARCHAR(50) NOT NULL, year INTEGER NOT NULL)")
    with open("books.csv", "r") as f:
        books = csv.reader(f)
        for i, book in enumerate(books):
            if i == 0:
                continue
            else:
                db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                           {"isbn": book[0], "title": book[1], "author": book[2], "year": book[3]})
                db.commit()
                print(f"Book# {i} added.")


if __name__ == "__main__":
    main()