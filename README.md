# Spotlight: Backend
![python-3.6.5](https://img.shields.io/badge/python-3.6.5-blue.svg)

## Server

* This repository would be deployed to Heroku server automatically when branch `master` is merged. 
* [Go to this server](https://spotlight-server.herokuapp.com)
* locally run server: `make run_server`

## Database

* Use `PostgreSQL` provided by Heroku.
* DB migration
  * create migration script: `make db_migrate`
  * upgrade: `make db_up` (please create migration script before this)
  * downgrade: `make db_down` (please remove useless script after this)

## Recommandation

* `make create_rec_table`
* Algorithm: ranking factorization recommender
    * Factor Dimension: 32
    * L2 Regularization on Factors: 1e-09
    * Solver used for training: sgd
    * L2 Regularization on Linear Coefficients: 1e-09
    * Maximum Number of Iterations: 25
* Process: content-based
    * use `jieba` to segment words
    * use TF-IDF to handle bag of words
    * use `turicreate.ranking_factorization_recommender` to train model

## Image Crawler

* `python crawler.py`
* Use "Google Image Search" to fill a vacancy of picture links.

## API

ps: Need cookie to identify user_id

### For Users
- [x] POST `/register`
    * post json body: `{"acc": "xxx", "pwd": "yyy", "name": "zzz"}`
- [x] POST `/login`
    * post json body: `{"acc": "xxx", "pwd": "yyy"}`
- [x] POST `/logout`
- [x] GET `/check_login`, need cookie
- [x] GET `/user/<int:user_id>`
- [x] GET `/users`
- [x] PUT `/own/user`, need cookie
- [x] GET `/stat/user/<int:user_id>`
    * keys of response: "published_projs_count", "collected_spots_count", "collected_projs_count", "projs_liked_count"

### For Spots
- [x] GET `/spot/<int:spot_id>`
    * example: `https://spotlight-server.herokuapp.com/spot/1`
- [x] GET `/spots?zone=xxx&zone=xxx&kw=xxx&page=xxx`
    * example: `https://spotlight-server.herokuapp.com/spots?zone=高雄市&zone=新竹市&page=0`
    * example: `https://spotlight-server.herokuapp.com/spots?zone=宜蘭縣&kw=夜市`
- [x] GET `/rec/spots?zone=xxx&zone=xxx&kw=xxx`, need cookie
    * example: `https://spotlight-server.herokuapp.com/rec/spots?zone=宜蘭縣&kw=夜市`
- [x] POST or DELETE `/like/spot/<int:spot_id>`, need cookie
    * example: `admin`, `https://spotlight-server.herokuapp.com/like/spot/5`
- [x] GET `/like/spots`, need cookie
    * example: `admin`, `https://spotlight-server.herokuapp.com/like/spots`
    * more info: `https://spotlight-server.herokuapp.com/like/spots?verbose=1`

### For Projects
- [x] POST or DELETE `/like/proj/<int:proj_id>`, need cookie
- [x] GET `/like/projs`, need cookie
    * more info: `https://spotlight-server.herokuapp.com/like/projs?verbose=1`
- [x] POST `/own/proj`, need cookie
    * post json body: `{"name": "旅行", "start_day": "2018/12/01 00:00:00", "tot_days": 3}`
- [x] GET `/own/projs`, need cookie
- [x] PUT `/own/proj/<int:proj_id>`, need cookie
    * put json body: `{"name": "CCC", "start_day": "2018/12/01 00:00:00", "tot_days": 2, "plan": [{"start_time": "08:00:00", "arrange": [{"spot_id": 1, "during": 60}, {"spot_id": 2, "during": 90}]}, {"start_time": "08:00:00", "arrange": [{"spot_id": 3, "during": 180}]}], "is_public": true}`
    * You can optionally choose `name`, `start_day`, `end_day`, `plan`, `is_public` to update
- [x] GET `/proj/<int:proj_id>`
    * example: `https://spotlight-server.herokuapp.com/proj/6`
- [x] DELETE `/proj/<int:proj_id>`, need cookie
- [x] GET `/projs?owner=xxx&only_public=true`
    * example: `https://spotlight-server.herokuapp.com/projs?owner=1`
