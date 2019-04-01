import os

from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_msearch import Search
from jieba.analyse import ChineseAnalyzer

# app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead and will be disabled
# by default in the future.  Set it to True to suppress this warning.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# cors
CORS(app)

# db
db = SQLAlchemy(app)

# whoosh
app.config['MSEARCH_INDEX_NAME'] = 'msearch'
app.config['MSEARCH_BACKEND'] = 'whoosh'
app.config['MSEARCH_ENABLE'] = True
search = Search(app, db=db, analyzer=ChineseAnalyzer())
