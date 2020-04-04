import random
import requests
from time import sleep

from .conf import BASE_URL, IMAGE_EXTENSIONS, SUBREDDIT
from .utils import get_datetime_from_unix


def make_api_request(end_timestamp: int = None, start_timestamp: int = None):
    query = BASE_URL.format(subreddit=SUBREDDIT)
    if start_timestamp:
        query += f'&after={start_timestamp}'
    if end_timestamp:
        query += f'&before={end_timestamp}'
    query_data = requests.get(query).json()['data']
    return query_data


def get_data(end_timestamp):
    data = make_api_request(end_timestamp=end_timestamp)
    if len(data) == 0:
        raise RuntimeError(f"No data was found for the given subreddit: '{SUBREDDIT}'")
    sleep(random.randint(1, 5))
    return data


def get_time_borders(data):
    first_post_timestamp = data[0]['created_utc']
    last_post_timestamp = data[-1]['created_utc']

    last_post_datetime = get_datetime_from_unix(last_post_timestamp)
    first_post_datetime = get_datetime_from_unix(first_post_timestamp)

    return first_post_datetime, last_post_datetime


def scrape_from_date_to_date(starttime_unix: int, endtime_unix: int) -> list:
    i = 0
    all_data = list()
    current_query_last_post_timestamp = endtime_unix
    while current_query_last_post_timestamp > starttime_unix:

        if i == 0:
            data = make_api_request(end_timestamp=endtime_unix)
        else:
            data = make_api_request(end_timestamp=current_query_last_post_timestamp)

        current_query_first_post_timestamp = data[0]['created_utc']
        current_query_first_post_datetime = get_datetime_from_unix(current_query_first_post_timestamp)

        current_query_last_post_timestamp = data[-1]['created_utc']
        current_query_last_post_datetime = get_datetime_from_unix(current_query_last_post_timestamp)

        print(
            f'Scraping step {i + 1} (since {current_query_last_post_datetime} till '
            f'{current_query_first_post_datetime})',
            len(data))

        all_data.extend(data)
        i += 1
    sleep(random.randint(1, 5))
    all_data = list(filter(lambda x: x['created_utc'] > starttime_unix, all_data))
    return all_data


def scrape_by_number_of_posts(endtime_unix: int, max_posts: int):
    i = 0
    all_data = list()
    posts_count = 0
    data = []
    while posts_count < max_posts:
        if i == 0:
            current_end_timestamp = endtime_unix
        else:
            current_end_timestamp = data[-1]['created_utc']
        data = get_data(end_timestamp=current_end_timestamp)
        posts_count += len(data)
        all_data.extend(data)
        query_first_post_datetime, query_last_post_datetime = get_time_borders(data)
        print(
            f'Scraping step {i + 1} (since {query_last_post_datetime} till '
            f'{query_first_post_datetime}):',
            len(data))
        i += 1
    return all_data[:max_posts]


def extract_information(posts):
    data_to_serialize = list()
    for post in posts:
        try:
            obj = {'post_id': post['id'],
                   'link': post['full_link'],
                   'timestamp': get_datetime_from_unix(post['created_utc']).strftime('%Y-%m-%d %H:%M:%S'),
                   'title': post['title'],
                   'text': post['selftext'],
                   'image': post['url'] if post['url'].split('.')[-1] in IMAGE_EXTENSIONS else '',
                   'subreddit': SUBREDDIT
                   }
            data_to_serialize.append(obj)
        except Exception as e:
            print(e)
    return data_to_serialize
