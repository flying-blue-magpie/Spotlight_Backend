import json
import hashlib
import os

from flask import request

from config import app
from config import db
from models import User
from models import Spot
from models import Project
from utils import json_default_handler

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


def _get_response(status, content=None):
    dict_ = dict()
    dict_['status'] = status
    if content:
        dict_['content'] = content
    state_code = 200 if status == 'success' else 404
    return (
        json.dumps(dict_, default=json_default_handler),
        state_code,
    )


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
    return _get_response('success')


@app.route('/login', methods=['POST'])
def login():
    content = request.get_json()
    acc = content['acc']
    pwd = content['pwd']
    user = User.query.filter_by(account=acc).first()
    if user and user.encoded_passwd == User.encode_passwd(pwd):
        res = app.make_response(
            _get_response('success', content={'user': user.account})
        )
        res.set_cookie(key=COOKIE_KEY, value=_get_cookie(user.id))
        return res
    else:
        return _get_response('fail')


@app.route('/logout', methods=['GET'])
def logout():
    res = app.make_response(_get_response('success'))
    res.set_cookie(key=COOKIE_KEY, value='', expires=0)
    return res


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return _get_response('success', content=user.to_dict())
    else:
        return _get_response('fail')


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    if users:
        return _get_response('success', content=[user.to_dict() for user in users])
    else:
        return _get_response('fail')


@app.route('/spot/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    spot = Spot.query.filter_by(id=spot_id).first()
    if spot:
        return _get_response('success', content=spot.to_dict())
    else:
        return _get_response('fail')


def _sort_by_keyword(keyword, spots):
    return spots


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

    if keyword:
        spots = _sort_by_keyword(keyword, spots)

    return _get_response('success', content=[spot.to_dict() for spot in spots])


@app.route('/proj/<int:proj_id>', methods=['GET'])
def get_proj(proj_id):
    proj = Project.query.filter_by(proj_id=proj_id).first()
    if proj:
        return _get_response('success', content=proj.to_dict())
    else:
        return _get_response('fail')


@app.route('/projs', methods=['GET'])
def get_projs():
    owner = request.args.get('owner')
    if owner:
        projs = Project.query.filter_by(owner=owner).all()
    else:
        projs = Project.query.all()

    if projs:
        return _get_response('success', content=[proj.to_dict() for proj in projs])
    else:
        return _get_response('fail')


if __name__ == '__main__':
    app.run()
