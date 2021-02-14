import json
import logging
import os
import time
import datetime

import tqdm as tqdm

from app.conf import DESIRED_POST_NUMBER, START_TIMESTAMP, END_TIMESTAMP, SUBREDDITS, BASE_URLS, KEYWORDS, \
    SCRAPE_SUBMISSION_COMMENTS
from app.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from app.utils import get_unix_timestamp

logger = logging.root
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

if not os.path.exists("data"):
    os.mkdir("data")


def get_parent_post_ids(file_name):
    with open(file_name, "r") as f:
        posts = json.load(f)
        ids = list(set([post["post_id"] for post in posts if post["num_comments"] > 0]))
    return ids


def run():
    look_back_timedelta = END_TIMESTAMP - START_TIMESTAMP
    day_delta = datetime.timedelta(1)

    if DESIRED_POST_NUMBER and START_TIMESTAMP:
        raise RuntimeError('You can either specify desired number of posts or start datetime')

    if START_TIMESTAMP:
        logger.info(
            f"Start scraping all the posts since {START_TIMESTAMP} till {END_TIMESTAMP} "
            f"in the following subreddits {SUBREDDITS} with the following keywords: {KEYWORDS}")

    start_time = time.time()

    this_day_timestamp = END_TIMESTAMP

    for i in range(look_back_timedelta.days):
        datetime_str = this_day_timestamp.strftime("%y-%m-%d")
        previous_day_timestamp = this_day_timestamp - day_delta
        file_name = f'data/data_{datetime_str}.json'
        logger.info(f"\nScraping from {previous_day_timestamp} to {this_day_timestamp}")

        unix_start = int(get_unix_timestamp(previous_day_timestamp))
        unix_end = int(get_unix_timestamp(this_day_timestamp))

        for subreddit in SUBREDDITS:
            for keyword in KEYWORDS:
                logger.debug(f"Scraping keyword '{keyword}'")
                item_type = "posts"
                url = BASE_URLS["posts"]
                run_search(url, item_type, subreddit, keyword, unix_start, unix_end, file_name)

                if SCRAPE_SUBMISSION_COMMENTS is True:
                    total_comments = 0
                    logger.debug("Scraping comments for posts")
                    item_type = "comments"
                    parent_post_ids = get_parent_post_ids(file_name)
                    parent_post_chunks = make_parent_post_filter_chunks(parent_post_ids)
                    for chu in tqdm.tqdm(parent_post_chunks):
                        url = BASE_URLS[item_type] + f'&link_id={chu}'
                        comments = run_search(url, item_type, subreddit, keyword, unix_start, unix_end, file_name,
                                              log=False)
                        total_comments += len(comments)
                    logger.info(
                        f"URL: {url}\nExtracted {total_comments} '{item_type}' from subreddit "
                        f"'{subreddit}' with a keyword '{keyword}'")

        this_day_timestamp = previous_day_timestamp

    end_time = time.time()
    logger.info(f"Total time:  {end_time - start_time} seconds")


def make_parent_post_filter_chunks(ids, chunk_size=20):
    chunks = [ids[l:l + chunk_size] for l in range(0, len(ids), chunk_size)]
    chunks = [",".join(chunk) for chunk in chunks]
    return chunks


def run_search(url, item_type, subreddit, keyword, unix_start, unix_end, file_name, log=True):
    logger.debug(f"Scraping type '{item_type}'")
    if DESIRED_POST_NUMBER:
        logger.debug(f"Scraping subreddit '{subreddit}' by max posts: {DESIRED_POST_NUMBER}")
        posts = scrape_by_number_of_posts(url, subreddit, keyword,
                                          endtime_unix=unix_end,
                                          max_posts=DESIRED_POST_NUMBER)
    else:
        logger.debug(f"Scraping posts in subreddit '{subreddit}' from date {START_TIMESTAMP}")
        posts = scrape_from_date_to_date(url, subreddit, keyword,
                                         starttime_unix=unix_start,
                                         endtime_unix=unix_end)
    if log:
        logger.info(
            f"URL: {url}\nExtracted {len(posts)} '{item_type}' from subreddit '{subreddit}' with a keyword '{keyword}'")

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

    return serialize_posts


if __name__ == '__main__':
    run()
