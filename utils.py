import json
import os

import requests

from datetime import datetime

DATETIME_STR_FMT = '%Y/%m/%d %H:%M:%S'


def json_default_handler(obj):
    if isinstance(obj, datetime):
        return obj.strftime(DATETIME_STR_FMT)


def strftime_to_datetime(s):
    return datetime.strptime(s, DATETIME_STR_FMT)


def upload_img_and_get_link(b64_code):
    headers = {'Authorization': 'Client-ID {}'.format(os.getenv('IMGUR_CLIENT'))}
    data = {'image': b64_code}
    resp = requests.post('https://api.imgur.com/3/upload', data=data, headers=headers)
    content = json.loads(resp.content)
    link = content['data']['link']
    del_hash = content['data']['deletehash']
    return link, del_hash
