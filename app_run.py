import json
import hashlib
import os
import re

from flask import request, make_response
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from config import app
from config import db
from models import User
from models import Spot
from models import Project
from models import FavoriteSpot
from models import FavoriteProject
from utils import json_default_handler
from utils import strftime_to_datetime
from utils import upload_img_and_get_link
from recommend import RecManager

COOKIE_KEY = 'spotlight-server-cookie'
REC_MANAGER = RecManager()
EMAIL_REGEX = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
PASSWORD_REGEX = r'^[a-zA-Z\d#$^+=!*()@%&].{0,20}$'
AREA_LIST = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市',
             '高雄市', '基隆市', '新竹市', '嘉義市', '新竹縣',
             '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣',
             '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣',
             '金門縣', '連江縣']


def _get_cookie(user_id):
    data = os.getenv('SECRET_TOKEN', '') + str(user_id)
    m = hashlib.md5()
    m.update(data.encode('utf8'))
    encoded_postfix = m.hexdigest()
    return '{}@{}'.format(user_id, encoded_postfix)


def _get_user_from_cookie(cookie):
    if not cookie:
        return None
    try:
        user_id, encoded_postfix = cookie.split('@')
        user_id = int(user_id)
        if _get_cookie(user_id) == cookie:
            return user_id
        else:
            return None
    except:
        return None


def _get_response(status, content=None, message=None):
    dict_ = dict()
    dict_['status'] = status
    if content is not None:
        dict_['content'] = content
    if message is not None:
        dict_['message'] = message
    state_code = 200
    resp = make_response(
        json.dumps(dict_, default=json_default_handler),
        state_code,
    )
    resp.mimetype = 'application/json'
    return resp


@app.route('/')
def hello_world():
    return 'Hello, this is a backend of Spotlight.'


@app.route('/register', methods=['POST'])
def register():
    content = request.get_json()
    acc = content['acc']
    pwd = content['pwd']
    name = content['name']
    if not acc or not re.match(EMAIL_REGEX, acc):
        return _get_response('fail', message='format of account is not corrent')
    if not pwd or not re.match(PASSWORD_REGEX, pwd):
        return _get_response('fail', message='format of password is not corrent')
    if User.query.filter_by(account=acc).first():
        return _get_response('fail', message='this account is used')

    user = User(acc, pwd, name)
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
        res = _get_response('success', content=user.to_dict())
        res.set_cookie(key=COOKIE_KEY, value=_get_cookie(user.id))
        return res
    else:
        return _get_response('fail')


@app.route('/logout', methods=['POST'])
def logout():
    res = _get_response('success')
    res.set_cookie(key=COOKIE_KEY, value='', expires=0)
    return res


@app.route('/check_login', methods=['GET'])
def check_login():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return _get_response('fail')
    return _get_response('success', content=user.to_dict())


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
        return _get_response('success', content=list())


@app.route('/own/user', methods=['PUT'])
def change_own_user():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    user = User.query.filter_by(id=user_id).first()

    content = request.get_json()
    if 'name' in content:
        user.name = content['name']
    if 'portrait' in content:
        b64_code = content['portrait']
        link, del_hash = upload_img_and_get_link(b64_code)
        user.portrait_link = link
        user.del_portrait = del_hash

    db.session.commit()
    return _get_response('success')


@app.route('/stat/user/<int:user_id>', methods=['GET'])
def get_user_statistic(user_id):

    published_projs_count = Project.query.filter_by(owner=user_id, is_public=True).count()

    collected_spots_count = FavoriteSpot.query.filter_by(user_id=user_id).count()
    collected_projs_count = FavoriteProject.query.filter_by(user_id=user_id).count()

    projs_liked_count = 0
    for p in Project.query.filter_by(owner=user_id).all():
        projs_liked_count += FavoriteProject.query.filter_by(proj_id=p.proj_id).count()

    return _get_response(
        'success',
        content=dict(
            published_projs_count=published_projs_count,
            collected_spots_count=collected_spots_count,
            collected_projs_count=collected_projs_count,
            projs_liked_count=projs_liked_count,
        )
    )


def _query_spot(spot_id):
    spot = Spot.query.filter_by(id=spot_id).first()
    return spot.to_dict() if spot else None


@app.route('/spot/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    content = _query_spot(spot_id)
    return _get_response('success', content=content) if content else _get_response('fail')


def _query_spots(zones=None, keyword=None, page_slice=None,
                 excluded_ids=None, included_ids=None, only_id=False):
    result = Spot.query

    if keyword:
        result = result.msearch(keyword, fields=['name', 'describe'])
    if zones:
        result = result.filter(Spot.zone.in_(zones))
    if excluded_ids:
        result = result.filter(~Spot.id.in_(excluded_ids))
    if included_ids:
        result = result.filter(Spot.id.in_(included_ids))

    if only_id:
        entities = [Spot.id]
        if page_slice:
            result = result.with_entities(*entities)[page_slice]
        else:
            result = result.with_entities(*entities)
        return [{'spot_id': tup[0]} for tup in result]

    if page_slice:
        spots = result[page_slice]
    else:
        spots = result.all()

    return [spot.to_dict() for spot in spots]


@app.route('/spots', methods=['GET'])
def get_spots():
    zones = request.args.getlist('zone')
    keyword = request.args.get('kw')
    page = int(request.args.get('page')) if request.args.get('page') else 0

    NUM_PER_PAGE = 1
    page_slice = slice(page*NUM_PER_PAGE, (page+1)*NUM_PER_PAGE)
    content = _query_spots(zones=zones, keyword=keyword, page_slice=page_slice)

    return _get_response('success', content=content)


@app.route('/rec/spots', methods=['GET'])
def get_rec_spots():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    zones = request.args.getlist('zone')
    keyword = request.args.get('kw')

    NUM_PER_PAGE = 1

    like_spot_ids = [
        like_spot.spot_id for like_spot
        in FavoriteSpot.query.filter_by(user_id=user_id)
                             .order_by(FavoriteSpot.created_time.desc()).all()
    ]
    selected_favorite_ids = like_spot_ids[:5]

    if REC_MANAGER.should_be_put(user_id, zones, keyword):
        spot_dict_list = _query_spots(zones=zones, keyword=keyword,
                                      excluded_ids=like_spot_ids, only_id=True)
        REC_MANAGER.put(
            user_id,
            [d['spot_id'] for d in spot_dict_list],
            selected_favorite_ids,
            zones=zones,
            keyword=keyword,
        )
        REC_MANAGER.update(user_id, selected_favorite_ids)

    if REC_MANAGER.should_be_updated(user_id, selected_favorite_ids):
        REC_MANAGER.update(user_id, selected_favorite_ids)

    selected_ids = REC_MANAGER.pop(user_id, NUM_PER_PAGE)
    content = _query_spots(included_ids=selected_ids)

    return _get_response('success', content=content)


@app.route('/like/spot/<int:spot_id>', methods=['POST', 'DELETE'])
def change_like_spot(spot_id):
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    favorite_spot = FavoriteSpot.query.filter_by(
        user_id=user_id, spot_id=spot_id).first()
    if request.method == 'POST':
        if not favorite_spot:
            favorite_spot = FavoriteSpot(user_id, spot_id)
            db.session.add(favorite_spot)
            db.session.commit()
    elif request.method == 'DELETE':
        if favorite_spot:
            db.session.delete(favorite_spot)
            db.session.commit()
    return _get_response('success')


@app.route('/like/spots', methods=['GET'])
def get_like_spots():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    verbose = int(request.args.get('verbose')) if 'verbose' in request.args else 0

    favorite_spots = FavoriteSpot.query.filter_by(user_id=user_id).all()
    if favorite_spots:
        favorite_spots_list = [fs.to_dict() for fs in favorite_spots]
        if verbose == 1:
            content = _get_spots_additional_info(favorite_spots_list)
        else:
            content = favorite_spots_list
        return _get_response('success', content=content)
    else:
        return _get_response('success', content=list())


@app.route('/own/spot', methods=['POST'])
def create_own_spot():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    try:
        content = request.get_json()
        name = content['name']
        zone = content.get('zone', '')
        if zone and zone not in (AREA_LIST + ['']):
            return _get_response('fail', message='zone is out of list')
        describe = content.get('describe')
        tel = content.get('tel')
        website = content.get('website')
        address = content.get('address')

        pic1_b64 = content.get('pic1')
        pic2_b64 = content.get('pic2')
        pic3_b64 = content.get('pic3')

        pic1, del_pic1 = upload_img_and_get_link(pic1_b64) if pic1_b64 else (None, None)
        pic2, del_pic2 = upload_img_and_get_link(pic2_b64) if pic2_b64 else (None, None)
        pic3, del_pic3 = upload_img_and_get_link(pic3_b64) if pic3_b64 else (None, None)
    except:
        return _get_response('fail', message='input is not correct')

    keyword = None
    px = None
    py = None

    spot = Spot(name, zone, describe, tel, website, keyword, address, pic1, pic2, pic3, px, py,
                del_pic1, del_pic2, del_pic3, user_id)
    db.session.add(spot)
    db.session.commit()

    # add to like-spot
    favorite_spot = FavoriteSpot(user_id, spot.id)
    db.session.add(favorite_spot)
    db.session.commit()

    return _get_response('success', content=spot.to_dict())


@app.route('/like/proj/<int:proj_id>', methods=['POST', 'DELETE'])
def change_like_proj(proj_id):
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    favorite_proj = FavoriteProject.query.filter_by(
        user_id=user_id, proj_id=proj_id).first()
    if request.method == 'POST':
        if not favorite_proj:
            favorite_proj = FavoriteProject(user_id, proj_id)
            db.session.add(favorite_proj)
            db.session.commit()
    elif request.method == 'DELETE':
        if favorite_proj:
            db.session.delete(favorite_proj)
            db.session.commit()
    return _get_response('success')


def _get_projs_additional_info(query_result):
    result = []
    for favorite_proj, proj in query_result:
        dict_ = favorite_proj.to_dict()
        dict_['proj_info'] = proj.to_dict()
        result.append(dict_)
    return result


@app.route('/like/projs', methods=['GET'])
def get_like_projs():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    verbose = int(request.args.get('verbose')) if 'verbose' in request.args else 0

    query_result = (db.session.query(FavoriteProject, Project)
                    .filter(FavoriteProject.proj_id == Project.proj_id)
                    .filter(FavoriteProject.user_id == user_id)
                    .filter(Project.is_public == True)
                    .all())

    if query_result:
        if verbose == 1:
            content = _get_projs_additional_info(query_result)
        else:
            favorite_projs, _ = zip(*query_result)
            content = [fs.to_dict() for fs in favorite_projs]
        return _get_response('success', content=content)
    else:
        return _get_response('success', content=list())


@app.route('/own/proj', methods=['POST'])
def create_own_proj():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    try:
        content = request.get_json()
        name = content['name']
        start_day = strftime_to_datetime(content['start_day'])
        tot_days = content['tot_days']
    except:
        return _get_response('fail', message='input is not correct')

    one_day_plan_list = [Project.OneDayPlan() for _ in range(tot_days)]

    params = [name, user_id, start_day, tot_days, one_day_plan_list]
    proj = Project(*params)
    db.session.add(proj)
    db.session.commit()
    return _get_response('success')


@app.route('/own/projs', methods=['GET'])
def get_own_projs():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    projs = Project.query.filter_by(owner=user_id).all()
    if projs:
        return _get_response('success', content=[proj.to_dict() for proj in projs])
    else:
        return _get_response('success', content=list())


@app.route('/own/proj/<int:proj_id>', methods=['PUT'])
def update_own_proj(proj_id):
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    proj = Project.query.filter_by(proj_id=proj_id, owner=user_id).first()
    if not proj:
        return _get_response('fail', message='project is not found')

    content = request.get_json()
    if 'name' in content:
        proj.name = content['name']
    if 'start_day' in content:
        proj.start_day = strftime_to_datetime(content['start_day'])
    if 'tot_days' in content:
        proj.tot_days = content['tot_days']
    if 'plan' in content:
        proj.plan = json.dumps(content['plan'], default=json_default_handler)
    if 'is_public' in content:
        proj.is_public = content['is_public']

    db.session.commit()
    return _get_response('success')


def _query_proj(proj_id):
    proj = Project.query.filter_by(proj_id=proj_id).first()
    return proj.to_dict() if proj else None


@app.route('/proj/<int:proj_id>', methods=['GET'])
def get_proj(proj_id):
    content = _query_proj(proj_id)
    return _get_response('success', content=content) if content else _get_response('fail')


@app.route('/proj/<int:proj_id>', methods=['DELETE'])
def delete_own_proj(proj_id):
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    proj = Project.query.filter_by(proj_id=proj_id, owner=user_id).first()
    if proj:
        for fav_proj in FavoriteProject.query.filter_by(proj_id=proj_id).all():
            db.session.delete(fav_proj)
        db.session.commit()
        db.session.delete(proj)
        db.session.commit()
        return _get_response('success')
    else:
        return _get_response('success', content=list())


@app.route('/projs', methods=['GET'])
def get_projs():
    only_public = request.args.get('only_public')
    owner = request.args.get('owner')
    if owner and only_public:
        projs = Project.query.filter_by(owner=owner, is_public=True).all()
    elif owner and not only_public:
        projs = Project.query.filter_by(owner=owner).all()
    elif not owner and only_public:
        projs = Project.query.filter_by(is_public=True).all()
    else:
        projs = Project.query.all()

    if projs:
        return _get_response('success', content=[proj.to_dict() for proj in projs])
    else:
        return _get_response('success', content=list())


def _get_spot_avg_vectors(spot_ids):
    spots = Spot.query.filter(Spot.id.in_(spot_ids)).all()
    arr = np.array([json.loads(spot.rec_factors) for spot in spots if spot.rec_factors])
    return np.average(arr, axis=0)


@app.route('/rec/projs', methods=['GET'])
def get_rec_projs():
    user_id = _get_user_from_cookie(request.cookies.get(COOKIE_KEY))
    if not user_id:
        return _get_response('fail', message='user_id is missing')

    projs = Project.query.filter_by(is_public=True).filter(Project.owner != user_id) \
                   .order_by(Project.update_time.desc()).all()

    favorite_spots = FavoriteSpot.query.filter_by(user_id=user_id).all()
    if not favorite_spots:
        content = [p.proj_id for p in projs]
        return _get_response('success', content=content)

    user_vector = _get_spot_avg_vectors([fs.spot_id for fs in favorite_spots])

    rating_list = []
    for proj in projs:
        spot_ids_in_proj = proj.get_all_spots()
        if spot_ids_in_proj:
            proj_vector = _get_spot_avg_vectors(spot_ids_in_proj)
            r = cosine_similarity([user_vector], [proj_vector])
        else:
            r = 0
        rating_list.append([r, proj.proj_id])
    content = [id for _, id in sorted(rating_list, reverse=True)]
    return _get_response('success', content=content)


def _get_spots_additional_info(favorite_spots_list):
    result = []
    for origin in favorite_spots_list:
        dict_ = dict(origin)
        dict_['spot_info'] = _query_spot(origin['spot_id'])
        result.append(dict_)
    return result


if __name__ == '__main__':
    app.run()
