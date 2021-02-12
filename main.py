import json
import logging
import os
import time
import datetime
from app.conf import DESIRED_POST_NUMBER, START_TIMESTAMP, END_TIMESTAMP, SUBREDDITS, BASE_URLS, KEYWORDS
from app.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from app.utils import get_unix_timestamp

logger = logging.root
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

if not os.path.exists("data"):
    os.mkdir("data")

if __name__ == '__main__':

    DAYS_BACK = END_TIMESTAMP - START_TIMESTAMP
    day_delta = datetime.timedelta(1)

    if DESIRED_POST_NUMBER and START_TIMESTAMP:
        raise RuntimeError('You can either specify desired number of posts or start datetime')

    posts = []

    if START_TIMESTAMP:
        logger.info(
            f"Start scraping all the posts since {START_TIMESTAMP} till {END_TIMESTAMP} "
            f"in the following subreddits {SUBREDDITS} with the following keywords: {KEYWORDS}")

    start_time = time.time()

    this_day_timestamp = END_TIMESTAMP

    for i in range(DAYS_BACK.days):
        previous_day_timestamp = this_day_timestamp - day_delta
        file_name = f'data/data_{this_day_timestamp.strftime("%y-%m-%d")}.json'
        logger.info(f"\nScraping from {previous_day_timestamp} to {this_day_timestamp}")

        unix_start = int(get_unix_timestamp(previous_day_timestamp))
        unix_end = int(get_unix_timestamp(this_day_timestamp))

        for subreddit in SUBREDDITS:
            for keyword in KEYWORDS:
                logger.debug(f"Scraping keyword '{keyword}'")
                for item_type in BASE_URLS:
                    logger.debug(f"Scraping type '{item_type}'")
                    if DESIRED_POST_NUMBER:
                        logger.debug(f"Scraping subreddit '{subreddit}' by max posts: {DESIRED_POST_NUMBER}")
                        posts = scrape_by_number_of_posts(BASE_URLS[item_type], subreddit, keyword,
                                                          endtime_unix=unix_end,
                                                          max_posts=DESIRED_POST_NUMBER)
                    else:
                        logger.debug(f"Scraping posts in subreddit '{subreddit}' from date {START_TIMESTAMP}")
                        posts = scrape_from_date_to_date(BASE_URLS[item_type], subreddit, keyword,
                                                         starttime_unix=unix_start,
                                                         endtime_unix=unix_end)

                    logger.info(
                        f"Extracted {len(posts)} '{item_type}' from subreddit '{subreddit}' with a keyword '{keyword}'")
                    serialize_posts = extract_information(subreddit, item_type, keyword, posts)

                    if os.path.exists(file_name):
                        with open(file_name, 'r') as f:
                            subreddit_data = json.load(f)
                            subreddit_data.extend(serialize_posts)
                        with open(file_name, 'w') as f:
                            json.dump(subreddit_data, f)
                    else:
                        with open(file_name, 'w') as f:
                            json.dump(serialize_posts, f)

        this_day_timestamp = previous_day_timestamp

    end_time = time.time()
    logger.info(f"Total time:  {end_time - start_time} seconds")
