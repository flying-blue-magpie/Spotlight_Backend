import json
import io

import pandas as pd

from config import db
from models import Spot

FILE_TW_SPOT = 'data/tw_spot.json'
AREA_LIST = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市',
             '高雄市', '基隆市', '新竹市', '嘉義市', '新竹縣',
             '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣',
             '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣',
             '金門縣', '連江縣']


def insert_tw_spot_to_db():

    with io.open(FILE_TW_SPOT, 'r', encoding='utf-8-sig') as fr:
        # print(json.load(fr))
        data = json.loads(fr.read())

        df = pd.read_json(json.dumps(data['XML_Head']['Infos']['Info']))

    for i, content in df.iterrows():
        if i <= 4220:
            continue

        name = content['Name']
        describe = content['Toldescribe']
        tel = content['Tel']
        website = content['Website']
        keyword = content['Keyword']
        address = content['Add']
        pic1 = content['Picture1']
        pic2 = content['Picture2']
        pic3 = content['Picture3']
        px = content['Px']
        py = content['Py']

        for a in AREA_LIST:
            if address.find(a) >= 0 or address.find(a.replace('臺', '台')) >= 0:
                zone = a
                break
        else:
            zone = ''

        params = [name, zone, describe, tel, website, keyword, address, pic1, pic2, pic3, px, py]
        try:
            spot = Spot(*params)
            db.session.add(spot)
            db.session.commit()
        except:
            print('error on row {}'.format(i))

        print('finish {}'.format(i))


if __name__ == '__main__':
    insert_tw_spot_to_db()
