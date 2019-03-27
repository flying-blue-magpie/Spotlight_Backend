import json
import hashlib
import os

from flask import request

from config import app
from config import db
from models import User
from models import Spot

COOKIE_KEY = 'spotlight-server-cookie'


def _get_cookie(user_id):
    data = os.getenv('SECRET_TOKEN', '') + str(user_id)
    m = hashlib.md5()
    m.update(data.encode('utf8'))
    encoded_postfix = m.hexdigest()
    return '{}@{}'.format(user_id, encoded_postfix)


def _get_user_from_cookie(cookie):
    try:
        user_id, encoded_postfix = cookie.split('@')
        user_id = int(user_id)
        if _get_cookie(user_id) == cookie:
            return user_id
        else:
            return None
    except:
        return None


@app.route('/')
def hello_world():
    return 'Hello, this is a backend of Spotlight.'


@app.route('/register', methods=['POST'])
def register():
    acc = request.form['acc']
    pwd = request.form['pwd']
    user = User(acc, pwd)
    db.session.add(user)
    db.session.commit()
    return json.dumps({'status': 'success'}), 200


@app.route('/login', methods=['POST'])
def login():
    acc = request.form['acc']
    pwd = request.form['pwd']
    user = User.query.filter_by(account=acc).first()
    if user and user.encoded_passwd == User.encode_passwd(pwd):
        res = app.make_response((json.dumps({'status': 'success'}), 200))
        res.set_cookie(key=COOKIE_KEY, value=_get_cookie(user.id))
        return res
    else:
        return json.dumps({'status': 'fail'}), 404


@app.route('/logout', methods=['GET'])
def logout():
    res = app.make_response(('', 200))
    res.set_cookie(key=COOKIE_KEY, value='', expires=0)
    return res


@app.route('/spot/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    spot = Spot.query.filter_by(id=spot_id).first()
    if spot:
        return json.dumps({'status': 'success', 'content': spot.to_dict()}), 200
    else:
        return json.dumps({'status': 'fail'}), 404


@app.route('/spots', methods=['GET'])
def get_spots():
    zones = request.args.getlist('zone')
    keyword = request.args.get('kw')
    page = int(request.args.get('page')) if request.args.get('page') else 0

    NUM_PER_PAGE = 100
    zones_slice = slice(page*NUM_PER_PAGE, (page+1)*NUM_PER_PAGE)
    if zones:
        spots = Spot.query.filter(Spot.zone.in_(zones))[zones_slice]
    else:
        spots = Spot.query[zones_slice]

    return json.dumps({'status': 'success', 'content': [spot.to_dict() for spot in spots]}), 200


if __name__ == '__main__':
    app.run()
