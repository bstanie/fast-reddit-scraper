import json
import logging
import os
import time
import datetime
from collections import defaultdict
import pandas as pd
import tqdm as tqdm
import argparse

from conf import SUBREDDITS, BASE_URLS, KEYWORDS, SCRAPE_SUBMISSION_COMMENTS
from app.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from app.utils import get_unix_timestamp

logger = logging.root
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

if not os.path.exists("data"):
    os.mkdir("data")


def get_parent_post_ids(file_name, keyword):
    with open(file_name, "r") as f:
        posts = json.load(f)
        ids = list(set([post["post_id"] for post in posts if post["num_comments"] > 0 and post["keyword"] == keyword]))
    return ids


def make_parent_post_filter_chunks(ids, chunk_size=20):
    chunks = [ids[l:l + chunk_size] for l in range(0, len(ids), chunk_size)]
    chunks = [",".join(chunk) for chunk in chunks]
    return chunks


def run_extraction(url, item_type, subreddit, keyword, unix_start, unix_end,
                   file_name, start_timestamp, log=True, desired_post_number=None, ):
    logger.debug(f"Scraping type '{item_type}'")
    if desired_post_number:
        logger.debug(f"Scraping subreddit '{subreddit}' by max posts: {desired_post_number}")
        posts = scrape_by_number_of_posts(url, subreddit, keyword,
                                          endtime_unix=unix_end,
                                          max_posts=desired_post_number)
    else:
        logger.debug(f"Scraping posts in subreddit '{subreddit}' from date {start_timestamp}")
        posts = scrape_from_date_to_date(url, subreddit, keyword,
                                         starttime_unix=unix_start,
                                         endtime_unix=unix_end)
    if log:
        logger.info(
            f"\nExtracted {len(posts)} '{item_type}' from subreddit '{subreddit}' with a keyword '{keyword}'")

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


def get_datetime_borders(args):
    start_date = args.start_date
    end_date = args.end_date

    if end_date:
        end_timestamp = datetime.datetime.strptime(end_date, "%y-%m-%d")
    else:
        dt_now = datetime.datetime.now()
        end_timestamp = datetime.datetime(dt_now.year,dt_now.month,dt_now.day)

    if start_date:
        start_timestamp = datetime.datetime.strptime(start_date, "%y-%m-%d")
    else:
        start_timestamp = end_timestamp - datetime.timedelta(1)

    return start_timestamp, end_timestamp


def run_extractor(start_timestamp, end_timestamp):
    DESIRED_POST_NUMBER = None

    look_back_timedelta = end_timestamp - start_timestamp
    day_delta = datetime.timedelta(1)

    if DESIRED_POST_NUMBER and start_timestamp:
        raise RuntimeError('You can either specify desired number of posts or start datetime')

    if start_timestamp:
        logger.info(
            f"Start scraping all the posts since {start_timestamp} till {end_timestamp} "
            f"in the following subreddits {SUBREDDITS} with the following keywords: {KEYWORDS}")

    log_start_time = time.time()
    this_day_timestamp = end_timestamp

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
                run_extraction(url, item_type, subreddit, keyword, unix_start, unix_end,
                               file_name, start_timestamp, log=True)

                if SCRAPE_SUBMISSION_COMMENTS is True:
                    total_comments = 0
                    logger.debug("Scraping comments for posts")
                    item_type = "comments"
                    parent_post_ids = get_parent_post_ids(file_name, keyword)
                    parent_post_chunks = make_parent_post_filter_chunks(parent_post_ids)
                    for chu in tqdm.tqdm(parent_post_chunks):
                        url = BASE_URLS[item_type] + f'&link_id={chu}'
                        comments = run_extraction(url, item_type, subreddit, keyword, unix_start, unix_end,
                                                  file_name, start_timestamp, log=False)
                        total_comments += len(comments)
                    logger.info(
                        f"Extracted {total_comments} '{item_type}' from subreddit "
                        f"'{subreddit}' with a keyword '{keyword}'")

        this_day_timestamp = previous_day_timestamp

    log_end_time = time.time()
    logger.info(f"Extraction finished. Time spent:  {log_end_time - log_start_time} seconds")


def make_report():
    dfs = []
    for file_name in list(os.walk("data"))[0][2]:
        file_path = f"data/{file_name}"
        with open(file_path, "r") as f:
            raw_data = json.load(f)
            data = []

            for item in raw_data:
                if type(item) == list:
                    data.extend(item)
                else:
                    data.append(item)

        result = defaultdict(lambda: defaultdict(int))

        for i in data:
            keyword = i["keyword"]
            comments = i["num_comments"]
            if i["type"] == "posts":
                result[keyword]["num_keyword_posts"] += 1
                result[keyword]["num_comments"] += comments
            elif i["type"] == "comments":
                result[keyword]["num_keyword_comments"] += 1

        df = pd.DataFrame(result).T
        df["date"] = file_path.split("_")[1].split(".")[0]

        dfs.append(df)

    stat_df = pd.concat(dfs).reset_index().rename(columns={"index": "keyword"}).sort_values(["keyword", "date"])
    stat_df = stat_df[["date", "keyword", "num_keyword_posts", "num_comments", "num_keyword_comments"]]
    stat_df.to_csv(f"reddit_crypto_stat.csv", index=False)


def run(args):
    start_timestamp, end_timestamp = get_datetime_borders(args)
    report_only = args.report_only
    if report_only:
        make_report()
    else:
        run_extractor(start_timestamp, end_timestamp)
        make_report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--report_only", help="Generate report from already scraped data",
                        required=False, default=False)
    parser.add_argument("-s", "--start_date", help="Scrape from date %y-%m-%d", required=False)
    parser.add_argument("-e", "--end_date", help="Scrape to date %y-%m-%d", required=False)
    _args = parser.parse_args()
    run(_args)
