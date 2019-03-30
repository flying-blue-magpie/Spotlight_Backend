# Spotlight: Backend
![python-3.7.1](https://img.shields.io/badge/python-3.7.1-blue.svg)

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

## API

- [x] `/register`, POST('acc', 'pwd'), response `('ok', 200)`
- [x] `/login`, POST('acc', 'pwd'), response `('pass', 200)` or `('fail',404)`
- [x] `/logout`, GET
- [x] `/check_login`, GET
- [ ] `/spot/<int:spot_id>`, GET, response `json(name, ..., like)`
    * example: `https://spotlight-server.herokuapp.com/spot/1`
- [x] `/spots?zone=xxx&zone=xxx&kw=xxx&page=xxx`, GET
    * example: `https://spotlight-server.herokuapp.com/spots?zone=高雄市&zone=新竹市&page=0`
- [x] `/like/spot/<int:spot_id>`, POST or DELETE, need cookie
    * example: `admin`, `https://spotlight-server.herokuapp.com/like/spot/5`
- [x] `/like/spots`, GET, need cookie
    * example: `admin`, `https://spotlight-server.herokuapp.com/like/spots`
- [ ] `/like/proj/<int:proj_id>`, POST or DELETE, need cookie
- [ ] `/like/projs`, GET, need cookie
- [ ] `/own/proj`, POST, need cookie
- [ ] `/own/projs`, GET, need cookie
- [ ] `/own/proj/<int:proj_id>`, PUT, need cookie
- [x] `/proj/<int:proj_id>`, GET
    * example: `https://spotlight-server.herokuapp.com/proj/6`
- [x] `/projs?owner=xxx`, GET
    * example: `https://spotlight-server.herokuapp.com/projs?owner=1`

ps: Need cookie to identify user_id
