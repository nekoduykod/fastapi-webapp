Run:
git clone https://github.com/nekoduykod/webapp_with_openai.git
pip install -r requirements.txt
cd webapp_fastapi_openai
uvicorn app.main:app --reload


pytest app/tests/test_main.py

Alembic:
alembic init alembic

Docker:
docker-compose run app alembic revision --autogenerate -m "New Migration" 
docker-compose run app alembic upgrade head

docker-compose build
docker-compose up

PostgreSQL pgadmin:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ DEFAULT current_timestamp
);

CREATE TABLE shortcuts (
    id SERIAL PRIMARY KEY,
    title VARCHAR UNIQUE NOT NULL,
    url VARCHAR NOT NULL,
    user_id INTEGER REFERENCES users(id),
    CONSTRAINT shorcut_title_key UNIQUE (title),
    CONSTRAINT shortcut_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);