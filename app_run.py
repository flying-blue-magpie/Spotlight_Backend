import os

from flask import Flask, request

from models import db
from models import User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled
# by default in the future.  Set it to True to suppress this warning.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


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
        return 'fail', 200


if __name__ == '__main__':
    app.run()
