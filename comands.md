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