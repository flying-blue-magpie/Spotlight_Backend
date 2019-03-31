from datetime import datetime

DATETIME_STR_FMT = '%Y/%m/%d %H:%M:%S'


def json_default_handler(obj):
    if isinstance(obj, datetime):
        return obj.strftime(DATETIME_STR_FMT)


def strftime_to_datetime(s):
    return datetime.strptime(s, DATETIME_STR_FMT)
