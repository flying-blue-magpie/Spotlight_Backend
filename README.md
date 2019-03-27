# Spotlight: Backend
![python-3.7.1](https://img.shields.io/badge/python-3.7.1-blue.svg)

## Server

* This repository would be deployed to Heroku server automatically when branch `master` is merged. 
* [Go to this server](https://spotlight-server.herokuapp.com)
* locally run server: `make run_server`

## Database

* Use `PostgreSQL` provided by Heroku.
* Info
  * User: `uzrocewaliwagy`
  * Password: `getenv('DB_PASSWD')`
  * DB: `d9sbr99mpdvmfl`
  * Host: `ec2-23-23-195-205.compute-1.amazonaws.com`
  * Port: `5432`
* DB migration
  * create migration script: `make db_migrate`
  * upgrade: `make db_up` (please create migration script before this)
  * downgrade: `make db_down` (please remove useless script after this)

## API

* `/register`, POST('acc', 'pwd'), response `('ok', 200)`
* `/login`, POST('acc', 'pwd'), response `('pass', 200)` or `('fail',404)`
* `/spot/<int:spot_id>`, GET, response `json(name, ..., like)`
* `/spots?zone=xxx&zone=xxx&kw=xxx&page=xxx`, GET
* `/like/spot/<int:spot_id>`, POST or DELETE, need cookie
* `/like/spots`, GET, need cookie
* `/like/proj/<int:proj_id>`, POST or DELETE, need cookie
* `/like/projs`, GET, need cookie
* `/own/proj`, POST, need cookie
* `/own/projs`, GET, need cookie
* `/own/proj/<int:proj_id>`, PUT, need cookie
* `/proj/<int:proj_id>`, GET
* `/projs`, GET

ps: Need cookie to identify user_id
