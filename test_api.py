import requests

GoodreadsKey = "6FmDrXrBHdMm22IUXa5Kw"

def main():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GoodreadsKey, "isbns": "0380795272"})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = res.json()
    print(data)

if __name__ == "__main__":
    main()