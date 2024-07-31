# Define the default target
.DEFAULT_GOAL := help

help:
	@echo "Usage: make <target>"
	@echo
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

install_deps:
	pip install -r requirements.txt

run_app:
	uvicorn app.main:app --reload

test:
	pytest app/tests/test_login.py
	pytest app/tests/test_register.py
	pytest app/tests/test_account.py
	pytest app/tests/test_shortcut.py
	pytest app/tests/test_chatgpt.py

alembic_init: # in alembic.ini => sqlalchemy.url = sqlite:///./database.db
	alembic init alembic

alembic_migrate: # alembic/env.py => from app.models.models import Base; target_metadata = Base.metadata
	alembic revision --autogenerate -m "New Migration"
	alembic upgrade head

docker_migrate:
	docker-compose run app alembic revision --autogenerate -m "New Migration"
	docker-compose run app alembic upgrade head

docker_build:
	docker-compose build

docker_up:
	docker-compose up

# Uncomment and use the following targets to create PostgreSQL tables
# create_tables:
#     psql -c "CREATE TABLE users ( \
#         id SERIAL PRIMARY KEY, \
#         username VARCHAR(255) UNIQUE NOT NULL, \
#         hashed_password VARCHAR(255) NOT NULL, \
#         email VARCHAR UNIQUE NOT NULL, \
#         created_at TIMESTAMPTZ DEFAULT current_timestamp, \
#         updated_at TIMESTAMPTZ DEFAULT current_timestamp \
#     );"
#     psql -c "CREATE TABLE shortcuts ( \
#         id SERIAL PRIMARY KEY, \
#         title VARCHAR UNIQUE NOT NULL, \
#         url VARCHAR NOT NULL, \
#         user_id INTEGER REFERENCES users(id), \
#         CONSTRAINT shortcut_title_key UNIQUE (title), \
#         CONSTRAINT shortcut_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) \
#     );"
