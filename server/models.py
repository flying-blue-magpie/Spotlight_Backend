import os
import hashlib

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(255), nullable=False)
    encoded_passwd = db.Column(db.String(255), nullable=False)

    def __init__(self, account, passwd):
        self.account = account
        self.encoded_passwd = User.encode_passwd(passwd)

    @classmethod
    def encode_passwd(cls, passwd):
        data = passwd + os.getenv('SECRET_TOKEN', '')
        m = hashlib.md5()
        m.update(data.encode('utf8'))
        encoded_passwd = m.hexdigest()
        return encoded_passwd
