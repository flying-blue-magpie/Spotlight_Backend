import os

from flask import Flask

from models import db

app = Flask(__name__)
POSTGRES = {
    'user': 'uzrocewaliwagy',
    'password': os.getenv('DB_PASSWD'),
    'db': 'd9sbr99mpdvmfl',
    'host': 'ec2-23-23-195-205.compute-1.amazonaws.com',
    'port': '5432',
}
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(db)s' % POSTGRES)

# SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled
# by default in the future.  Set it to True to suppress this warning.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)


@app.route('/')
def hello_world():
    return 'Hello, this is a backend of Spotlight.'


if __name__ == '__main__':
    app.run()
