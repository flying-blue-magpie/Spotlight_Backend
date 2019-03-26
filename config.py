import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled
# by default in the future.  Set it to True to suppress this warning.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
