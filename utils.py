from datetime import datetime, timedelta


def json_default_handler(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    elif isinstance(obj, timedelta):
        return obj.total_seconds() // 60
