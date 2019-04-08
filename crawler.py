import os
import re
import urllib
from urllib.parse import quote
import traceback
import uuid

from user_agent import generate_user_agent
from PIL import Image

from models import db
from models import Spot

GOOGLE_IMAGE_FMT = 'https://www.google.com/search?q={keyword}&source=lnms&tbm=isch'
NEW_IMAGE_ROOT = './new_img'
RAW_IMAGE_ROOT = './raw_img'


def _download_page(url):
    try:
        headers = {
            'User-Agent': generate_user_agent(),
            'Referer': 'https://www.google.com',
        }
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)
        return str(resp.read())
    except Exception:
        print('error while downloading page {0}'.format(url))
        return None


def _parse_page(page_content):
    if page_content:
        link_list = re.findall('"ou":"(.*?)"', page_content)
        if len(link_list) == 0:
            print('get 0 links')
            return list()
        else:
            return link_list
    else:
        return list()


def try_to_download_image(link, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        req = urllib.request.Request(link, headers={"User-Agent": generate_user_agent()})
        response = urllib.request.urlopen(req, timeout=10)
        if not (200 <= response.getcode() < 300):
            print('Error: status code is not 2xx')
            return 'fail'
        data = response.read()
        file_path = '{}/{}.jpg'.format(folder, str(uuid.uuid4()))
        with open(file_path, 'wb') as fw:
            fw.write(data)
        Image.open(file_path)
    except urllib.error.URLError as e:
        print('Error: URLError while downloading image {0}\nreason:{1}'.format(link, e.reason))
    except urllib.error.HTTPError as e:
        print('Error: HTTPError while downloading image {0}\nhttp code {1}, reason:{2}'.format(link, e.code, e.reason))
    except IOError:
        print('Error: Image can not be open')
        os.remove(file_path)
    except Exception as e:
        print('Error: Unexpeted error while downloading image {0}\nerror type:{1}, args:{2}'.format(link, type(e), e.args))
    else:
        return 'success'
    return 'fail'


def get_image_links(keyword):
    print('Process keyword: {}'.format(keyword))
    quoted_keyword = quote(keyword)
    url = GOOGLE_IMAGE_FMT.format(keyword=quoted_keyword)
    page_content = _download_page(url)
    image_links = _parse_page(page_content)

    return image_links


def main():
    count = 0
    for spot in Spot.query:
        count += 1
        print('[count] {}'.format(count))

        try:
            if spot.zone:
                keyword = spot.name + ' ' + spot.zone
            else:
                keyword = spot.name

            image_links = get_image_links(keyword)
            if not image_links:
                continue

            sub_folder_name = '{}-{}'.format(spot.id, keyword)
            raw_folder = os.path.join(RAW_IMAGE_ROOT, sub_folder_name)
            new_folder = os.path.join(NEW_IMAGE_ROOT, sub_folder_name)

            if image_links and (not spot.pic1
                                or try_to_download_image(spot.pic1, raw_folder) == 'fail'):
                while len(image_links) > 0:
                    link = image_links.pop(0)
                    if len(link) > 500:
                        continue
                    if try_to_download_image(link, new_folder) == 'success':
                        spot.pic1 = link
                        print('update pic1: {}'.format(spot.pic1))
                        break

            if image_links and (not spot.pic2
                                or try_to_download_image(spot.pic2, raw_folder) == 'fail'):
                while len(image_links) > 0:
                    link = image_links.pop(0)
                    if len(link) > 500:
                        continue
                    if try_to_download_image(link, new_folder) == 'success':
                        spot.pic2 = link
                        print('update pic2: {}'.format(spot.pic2))
                        break

            if image_links and (not spot.pic3
                                or try_to_download_image(spot.pic3, raw_folder) == 'fail'):
                while len(image_links) > 0:
                    link = image_links.pop(0)
                    if len(link) > 500:
                        continue
                    if try_to_download_image(link, new_folder) == 'success':
                        spot.pic3 = link
                        print('update pic3: {}'.format(spot.pic3))
                        break

            db.session.commit()
        except Exception as ex:
            print('error on row {}'.format(spot.id))
            traceback.print_exc()
            print(str(ex))

        print('finish id {}'.format(spot.id))


if __name__ == '__main__':
    main()
