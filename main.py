import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates 
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
templates = Jinja2Templates(directory="templates")

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])

@app.get('/', response_class=HTMLResponse)
async def home(request: Request):    # DO I NEED ASYNC HERE and next snippets
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/login', response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get('/register', response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/add-user/", response_model=SchemaUsers)
def add_user(user: SchemaUsers):
    db_user = ModelUsers(id=user.id, username=user.username, password=user.password, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user

@app.get("/users/")
def get_users():
    users = db.session.query(Users).all()
    return users

@app.post("/add-stat/", response_model=SchemaStatistics)
def add_statistic(stat: SchemaStatistics):
    db_statistics = ModelStatistics(id=stat.id, user_id=stat.user_id, page_transitions=stat.page_transitions, 
                                    vpn_site_transitions=stat.vpn_site_transitions, data_sent=stat.data_sent, 
                                    data_received=stat.data_received)
    db.session.add(db_statistics)
    db.session.commit()
    return db_statistics

@app.get("/stats/")
def get_stat():
    stats = db.session.query(Statistics).all()
    return stats