
.PHONY: run_server
run_server:
	python ./server/app_run.py

.PHONY: db_migrate
db_migrate:
	python ./server/manage.py db migrate

.PHONY: db_up
db_up:
	python ./server/manage.py db upgrade

.PHONY: db_down
db_down:
	python ./server/manage.py db downgrade
