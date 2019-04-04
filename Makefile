
.PHONY: run_server
run_server:
	python ./app_run.py

.PHONY: db_migrate
db_migrate:
	python ./manage.py db migrate

.PHONY: db_up
db_up:
	python ./manage.py db upgrade

.PHONY: db_down
db_down:
	python ./manage.py db downgrade

.PHONY: create_rec_table
create_rec_table:
	python ./recommend.py
