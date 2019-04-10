import os
import hashlib
import json

from sqlalchemy import func

from config import db
from utils import json_default_handler


class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), nullable=False, unique=True)
    encoded_passwd = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    protrait = db.Column(db.LargeBinary())

    def __init__(self, account, passwd, name):
        self.account = account
        self.encoded_passwd = User.encode_passwd(passwd)
        self.name = name

    @classmethod
    def encode_passwd(cls, passwd):
        data = passwd + os.getenv('SECRET_TOKEN', '')
        m = hashlib.md5()
        m.update(data.encode('utf8'))
        encoded_passwd = m.hexdigest()
        return encoded_passwd

    def to_dict(self):
        return dict(
            user_id=self.id,
            account=self.account,
            name=self.name,
            protrait=self.protrait,
        )


class Spot(db.Model):
    __tablename__ = 'Spots'
    __searchable__ = ['name', 'describe']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    zone = db.Column(db.String(20), nullable=False)
    describe = db.Column(db.String(5000))
    tel = db.Column(db.String(255))
    website = db.Column(db.String(500))
    keyword = db.Column(db.String(255))
    address = db.Column(db.String(500))
    pic1 = db.Column(db.String(500))
    pic2 = db.Column(db.String(500))
    pic3 = db.Column(db.String(500))
    px = db.Column(db.Float(precision=18))
    py = db.Column(db.Float(precision=18))
    rec_table = db.Column(db.String(50000))
    rec_factors = db.Column(db.String(2000))

    def __init__(self, name, zone, describe, tel, website, keyword, address, pic1, pic2, pic3, px, py):
        self.name = name
        self.zone = zone
        self.describe = describe
        self.tel = tel
        self.website = website
        self.keyword = keyword
        self.address = address
        self.pic1 = pic1
        self.pic2 = pic2
        self.pic3 = pic3
        self.px = px
        self.py = py

    def to_dict(self):
        return dict(
            spot_id=self.id,
            name=self.name,
            zone=self.zone,
            describe=self.describe,
            tel=self.tel,
            website=self.website,
            keyword=self.keyword,
            address=self.address,
            pic=[p for p in [self.pic1, self.pic2, self.pic3] if p],
            px=self.px,
            py=self.py,
            like_num=self.count_like_num(),
        )

    def count_like_num(self):
        return FavoriteSpot.query.filter_by(spot_id=self.id).count()


class Project(db.Model):
    __tablename__ = 'Projects'

    proj_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey("Users.id"), nullable=False)
    start_day = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    tot_days = db.Column(db.Integer, nullable=False)
    plan = db.Column(db.String(5000), nullable=False)
    created_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False,
                             server_default=func.now())
    update_time = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False,
        server_default=func.now(), onupdate=func.current_timestamp()
    )
    is_public = db.Column(db.Boolean, server_default=db.text('FALSE'), nullable=False)

    def __init__(self, name, owner, start_day, tot_days, one_day_plan_list):
        self.name = name
        self.owner = owner
        self.start_day = start_day
        self.tot_days = tot_days
        self.plan = json.dumps(
            [p.to_dict() for p in one_day_plan_list], default=json_default_handler
        )

    def to_dict(self):
        return dict(
            proj_id=self.proj_id,
            name=self.name,
            owner=self.owner,
            start_day=self.start_day,
            tot_days=self.tot_days,
            plan=json.loads(self.plan),
            created_time=self.created_time,
            update_time=self.update_time,
            is_public=self.is_public,
            like_num=self.count_like_num(),
        )

    def count_like_num(self):
        return FavoriteProject.query.filter_by(proj_id=self.proj_id).count()

    def get_all_spots(self):
        plan = json.loads(self.plan)
        spot_ids = set()
        for day_dict in plan:
            for spot_dict in day_dict['arrange']:
                spot_ids.add(spot_dict['spot_id'])
        return list(spot_ids)

    class OneDayPlan:
        def __init__(self):
            self.start_time = '08:00:00'
            self._arrange = []

        def add_spot(self, spot, during_min):
            self._arrange.append(
                {
                    'spot_id': spot.id,
                    'during': during_min,
                }
            )

        def to_dict(self):
            return dict(
                start_time=self.start_time,
                arrange=self._arrange,
            )

        @classmethod
        def from_dict(cls, d):
            obj = Project.OneDayPlan()
            obj.start_time = d['start_time']
            obj._arrange = d['arrange']
            return obj


class FavoriteSpot(db.Model):
    __tablename__ = 'FavoriteSpots'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('Spots.id'), nullable=False)
    created_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False,
                             server_default=func.now())

    def __init__(self, user_id, spot_id):
        self.user_id = user_id
        self.spot_id = spot_id

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            spot_id=self.spot_id,
            created_time=self.created_time,
        )


class FavoriteProject(db.Model):
    __tablename__ = 'FavoriteProjects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    proj_id = db.Column(db.Integer, db.ForeignKey('Projects.proj_id'), nullable=False)
    created_time = db.Column(db.TIMESTAMP(timezone=True), nullable=False,
                             server_default=func.now())

    def __init__(self, user_id, proj_id):
        self.user_id = user_id
        self.proj_id = proj_id

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            proj_id=self.proj_id,
            created_time=self.created_time,
        )


class RecRecord(db.Model):
    __tablename__ = 'RecRecords'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False, unique=True)
    rec_list = db.Column(db.String(50000), nullable=False)
    last_favorite_list = db.Column(db.String(300), nullable=False)
    last_query_zones = db.Column(db.String(2000))
    last_query_keyword = db.Column(db.String(300))

    def __init__(self, user_id, rec_list, last_favorite_list,
                 last_query_zones=None, last_query_keyword=None):
        self.user_id = user_id
        self.set_rec_list(rec_list)
        self.set_last_favorite_list(last_favorite_list)
        self.set_last_query_zones(last_query_zones)
        self.last_query_keyword = last_query_keyword

    def to_dict(self):
        return dict(
            user_id=self.user_id,
            rec_list=json.loads(self.rec_list),
            last_favorite_list=json.loads(self.last_favorite_list),
            last_query_zones=json.loads(self.last_query_zones) if self.last_query_zones else None,
            last_query_keyword=self.last_query_keyword,
        )

    def set_rec_list(self, rec_list):
        self.rec_list = json.dumps(rec_list)

    def set_last_favorite_list(self, last_favorite_list):
        self.last_favorite_list = json.dumps(last_favorite_list)

    def set_last_query_zones(self, last_query_zones):
        self.last_query_zones = json.dumps(last_query_zones) if last_query_zones else None
