import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates 
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os
 
from models import Users
from models import Users as ModelUsers
from models import Statistics
from models import Statistics as ModelStatistics
from models import Site as ModelSite

from schema import Users as SchemaUsers
from schema import Statistics as SchemaStatistics

load_dotenv(".env")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.add_middleware(SessionMiddleware, secret_key="bananabomb")

@app.get('/', response_class=HTMLResponse)
async def home(request: Request):     # I can use only def in these snippets
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register', response_class=HTMLResponse)
async def registr_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
                                      
@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, 
                   username: str = Form(...), 
                   password: str = Form(...), 
                   email: str = Form(...)):
    existing_user = db.session.query(Users).filter(Users.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already exists"})
    db_user = ModelUsers(username=username, password=password, email=email)
    db.session.add(db_user)
    db.session.commit()
    print("Registration successful. Redirecting to login.")
    return RedirectResponse(url="/login", status_code=303)

@app.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, 
              username: str = Form(...), 
              password: str = Form(...)):
  existing_user = db.session.query(Users).filter(Users.username == username, Users.password == password).first()
  if existing_user:
      request.session["user"] = {"username": username, "email": existing_user.email, "id": existing_user.id}
      response = RedirectResponse(url="/account", status_code=303)
      return response
  else: 
      return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid username or password"})


@app.get('/account', response_class=HTMLResponse)
async def account_page(request: Request):
  user = request.session.get("user")
  if user:
      return templates.TemplateResponse("account.html", {"request": request, "user": user, "error": None})
  else:
      return templates.TemplateResponse("account.html", {"request": request, "user": None, "error": "You are not logged in"})
  
@app.post('/account', response_class=HTMLResponse)
async def change_pass(request: Request, 
                    current_password: str = Form(...), 
                    new_password: str = Form(...), 
                    confirm_password: str = Form(...)):
 user = {"username": request.session.get("user")["username"], "password": current_password}
 existing_user = db.session.query(Users).filter(Users.username == user["username"], Users.password == user["password"]).first()
 if not existing_user:
     return templates.TemplateResponse("account.html", {"request": request, "error": "Incorrect current password"})
 if new_password != confirm_password:
     return templates.TemplateResponse("account.html", {"request": request, "error": "New password and confirm password do not match"})
 existing_user.password = new_password
 db.session.commit() 
 return RedirectResponse(url="/account", status_code=303)

@app.post("/create_site")
async def create_site(request: Request, site_name: str = Form(...), site_url: str = Form(...)):
  user = request.session.get("user")
  if not user:
      return RedirectResponse("/login")
  site = ModelSite(name=site_name, url=site_url, user_id=user["id"])
  db.session.add(site)
  db.session.commit()
  return RedirectResponse(url="/account", status_code=303)

@app.get("/update_sites")
async def update_sites(request: Request):
 user = request.session.get("user")
 if user:
   user_id = user["id"]
   sites = db.session.query(ModelSite).filter(ModelSite.user_id == user_id).all()
   return {"sites": [{"name": site.name, "id": site.id} for site in sites]}
 else:
   return {"error": "You are not logged in"}

@app.get("/go-to-site/{site_id}")
async def go_to_site(request: Request, site_id: int):
   user = request.session.get("user")
   if not user:
       return RedirectResponse("/login")
   site = db.session.query(ModelSite).filter(ModelSite.id == site_id, ModelSite.user_id == user["id"]).first()
   if site:
       return RedirectResponse(site.url)
   else:
       return RedirectResponse("/account")
 
 # Will think how to implement this below
@app.get("/{user_site_name}/{routes_on_original_site}", response_class=RedirectResponse)
async def redirect_to_site(user_site_name: str, routes_on_original_site: str, request: Request):
 user = request.session.get("user")
 if not user:
    return RedirectResponse("/login")
 site = db.session.query(ModelSite).filter(ModelSite.name == user_site_name, ModelSite.user_id == user["id"]).first()
 if site:
     return RedirectResponse(f"{site.url}/{routes_on_original_site}")
 else:
    return RedirectResponse("/account")
 

# Next snippets are for http://127.0.0.1:8000/docs#/ 
@app.post("/add-user/", response_model=SchemaUsers)
def add_user(user: SchemaUsers):
    db_user = ModelUsers(username=user.username, password=user.password, email=user.email)
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)