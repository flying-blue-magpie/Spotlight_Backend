from flask import request

from config import app
from config import db
from models import User
from models import Spot


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
    return 'ok', 200


@app.route('/login', methods=['POST'])
def login():
    acc = request.form['acc']
    pwd = request.form['pwd']
    user = User.query.filter_by(account=acc).first()
    if user and user.encoded_passwd == User.encode_passwd(pwd):
        return 'pass', 200
    else:
        return 'fail', 404


@app.route('/spot/<int:spot_id>', methods=['GET'])
def get_spot(spot_id):
    spot = Spot.query.filter_by(id=spot_id).first()
    if spot:
        j_str = spot.to_json()
        return j_str, 200
    else:
        return '', 404


if __name__ == '__main__':
    app.run()
