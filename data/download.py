import os
import json
import io

from tqdm import tqdm
from six.moves.urllib.request import urlretrieve
import pandas as pd


URL_TW_SPOT = 'https://gis.taiwan.net.tw/XMLReleaseALL_public/scenic_spot_C_f.json'
FILE_TW_SPOT = 'tw_spot.json'


def get_progress_callback():
    progressbar = None

    def _show_progress(count, block_size, total_size):
        nonlocal progressbar

        if progressbar is None:
            progressbar = tqdm(total=total_size)

        downloaded = block_size * count
        if downloaded <= total_size:
            progressbar.update(block_size)
        else:
            progressbar.close()
            progressbar = None

    return _show_progress


def maybe_download_tw_spot():
    if not os.path.exists(FILE_TW_SPOT):
        url = URL_TW_SPOT
        print('download from {}'.format(url))
        progress_callback = get_progress_callback()
        filename, _ = urlretrieve(url, FILE_TW_SPOT, progress_callback)


maybe_download_tw_spot()
with io.open(FILE_TW_SPOT, 'r', encoding='utf-8-sig') as fr:
    # print(json.load(fr))
    data = json.loads(fr.read())

    df = pd.read_json(json.dumps(data['XML_Head']['Infos']['Info']))

    print(df.columns)