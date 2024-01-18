pip install --upgrade pip
pip install -r requirements.txt


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT current_timestamp,
    updated_at TIMESTAMPTZ DEFAULT current_timestamp
);

CREATE TABLE shortcuts (    #
    id SERIAL PRIMARY KEY,
    title VARCHAR UNIQUE NOT NULL,  #
    url VARCHAR NOT NULL,
    user_id INTEGER REFERENCES users(id),
    CONSTRAINT shorcut_title_key UNIQUE (title),
    CONSTRAINT shortcut_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)
);


cd webapp_with_openai
uvicorn app.main:app --reload


alembic init alembic

docker-compose run app alembic revision --autogenerate -m "New Migration" 

docker-compose run app alembic upgrade head

docker-compose build

docker-compose up