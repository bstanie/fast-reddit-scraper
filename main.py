from app.conf import DESIRED_POST_NUMBER, START_TIMESTAMP, END_TIMESTAMP, SUBREDDIT
from app.db import generate_db, write_to_db
from app.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from app.utils import get_unix_timestamp

# To change configurations proceed to app/conf.py and follow instructions

if __name__ == '__main__':
    if DESIRED_POST_NUMBER and START_TIMESTAMP:
        raise RuntimeError('You can either specify desired number of posts or start datetime')

    unix_end = int(get_unix_timestamp(END_TIMESTAMP))
    if DESIRED_POST_NUMBER:
        print(f"Scraping subreddit '{SUBREDDIT}' by max posts: {DESIRED_POST_NUMBER}")
        posts = scrape_by_number_of_posts(endtime_unix=unix_end, max_posts=DESIRED_POST_NUMBER)
    elif START_TIMESTAMP is not None:
        print(f"Scraping all posts in subreddit '{SUBREDDIT}' from date {START_TIMESTAMP}")
        unix_start = int(get_unix_timestamp(START_TIMESTAMP))
        posts = scrape_from_date_to_date(starttime_unix=unix_start, endtime_unix=unix_end)

    print("Total posts extracted:", len(posts))
    serialize_posts = extract_information(posts)
    db_connection = generate_db('db.sqlite')
    cur = db_connection.cursor()
    write_to_db(cur, serialize_posts)
    print("Successfully update DB. Enjoy")