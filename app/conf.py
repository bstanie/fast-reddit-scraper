from datetime import datetime

# --------------------CHANGE HERE------------------------------------------

# Define subreddit
SUBREDDIT = 'todayilearned'

# You can EITHER choose desired posts number (i.e 10000) or limit posts from start date and time
DESIRED_POST_NUMBER = 15000
START_TIMESTAMP = 0  # example of date: START_TIMESTAMP = datetime(2020,1,1)

# You can optionally choose end date as well. Automatically it will be the current date and time
END_TIMESTAMP = datetime.now()  # example of arbitrary date: END_TIMESTAMP = datetime(2020,3,1)

# -----------------------------------------------------------------------------------


BASE_URL = 'https://api.pushshift.io/reddit/submission/search/?subreddit={subreddit}' \
           '&size=1000'

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'gif', 'png']
