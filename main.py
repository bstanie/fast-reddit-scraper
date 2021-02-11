import json
import os

from app.conf import DESIRED_POST_NUMBER, START_TIMESTAMP, END_TIMESTAMP, SUBREDDITS, BASE_URLS, KEYWORDS
from app.scraper import scrape_by_number_of_posts, scrape_from_date_to_date, extract_information
from app.utils import get_unix_timestamp

if __name__ == '__main__':
    if DESIRED_POST_NUMBER and START_TIMESTAMP:
        raise RuntimeError('You can either specify desired number of posts or start datetime')

    posts = []
    unix_end = int(get_unix_timestamp(END_TIMESTAMP))
    if START_TIMESTAMP:
        print(
            f"Scrape all the posts since {START_TIMESTAMP} till {END_TIMESTAMP} in the following subreddits {SUBREDDITS}")

    for subreddit in SUBREDDITS:
        for keyword in KEYWORDS:
            print(f"Scraping keyword '{keyword}'")
            for item_type in BASE_URLS:
                print(f"Scraping type '{item_type}'")
                if DESIRED_POST_NUMBER:
                    print(f"Scraping subreddit '{subreddit}' by max posts: {DESIRED_POST_NUMBER}")
                    posts = scrape_by_number_of_posts(BASE_URLS[item_type], subreddit, keyword, endtime_unix=unix_end,
                                                      max_posts=DESIRED_POST_NUMBER)
                elif START_TIMESTAMP is not None:
                    print(f"Scraping posts in subreddit '{subreddit}' from date {START_TIMESTAMP}")
                    unix_start = int(get_unix_timestamp(START_TIMESTAMP))
                    posts = scrape_from_date_to_date(BASE_URLS[item_type], subreddit, keyword,
                                                     starttime_unix=unix_start,
                                                     endtime_unix=unix_end)

                print(f"Extracted {len(posts)} '{item_type}' from subreddit '{subreddit}'")
                serialize_posts = extract_information(subreddit, item_type, keyword, posts)
                if os.path.exists(f"data.json"):
                    with open(f"data.json", 'r') as f:
                        subreddit_data = json.load(f)
                        subreddit_data.append(serialize_posts)
                    with open(f"data.json", 'w') as f:
                        json.dump(subreddit_data, f)
                else:
                    with open(f"data.json", 'w') as f:
                        json.dump(serialize_posts, f)
