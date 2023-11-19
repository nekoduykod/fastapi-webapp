import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv
import os

from models import Users
from models import Users as ModelUsers
from models import Statistics
from models import Statistics as ModelStatistics

from schema import Users as SchemaUsers
from schema import Statistics as SchemaStatistics

load_dotenv(".env")

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


@app.get('/')
async def root():
    return {"message": "Hello World"}

@app.post("/add-user/", response_model=SchemaUsers)
def register_user(user: SchemaUsers):
    db_user = ModelUsers(id=user.id, username=user.username, password=user.password, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user

@app.post("/add-stat/", response_model=SchemaStatistics)
def add_statistic(stat: SchemaStatistics):
    db_statistics = ModelStatistics(id=stat.id, user_id=stat.user_id, page_transitions=stat.page_transitions, 
                                    vpn_site_transitions=stat.vpn_site_transitions, data_sent=stat.data_sent, 
                                    data_received=stat.data_received)
    db.session.add(db_statistics)
    db.session.commit()
    return db_statistics

@app.get("/users/")
def get_users():
    users = db.session.query(Users).all()
    return users