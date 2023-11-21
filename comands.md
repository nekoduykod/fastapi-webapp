pip install fastapi fastapi-sqlalchemy pydantic alembic psycopg2 uvicorn python-dotenv starlette

uvicorn main:app --reload

docker-compose run app alembic revision --autogenerate -m "New Migration" 

docker-compose run app alembic upgrade head

docker-compose build 
docker-compose up