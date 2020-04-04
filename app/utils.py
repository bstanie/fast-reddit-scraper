from datetime import datetime


def get_unix_timestamp(dt: datetime):
    unix_timestamp = (dt - datetime(1970, 1, 1)).total_seconds()
    return unix_timestamp


def get_datetime_from_unix(unix_timestamp):
    dt = datetime.fromtimestamp(unix_timestamp)
    return dt
