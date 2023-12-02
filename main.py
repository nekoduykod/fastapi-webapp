import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates 
from fastapi_sqlalchemy import DBSessionMiddleware, db
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import openai
from openai import OpenAI
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

client = OpenAI()

app.mount("/static", StaticFiles(directory="static"), name="static")
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
    request.session["error"] = "Incorrect current password"
    return templates.TemplateResponse("account.html", {"request": request, "user": user, "error": request.session.get('error')})
 if new_password != confirm_password:
    request.session["error"] = "New password and confirm password do not match"
    return templates.TemplateResponse("account.html", {"request": request, "user": user, "error": request.session.get('error')})
 else:
    existing_user.password = new_password
    db.session.commit() 
    request.session["error"] = "Password changed successfully"
    return templates.TemplateResponse("account.html", {"request": request, "user": user, "error": request.session.get('error')})


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "not-set-api-key")

class OpenAIDependency:
   def __init__(self, api_key: str = Depends(get_openai_api_key)):
      self.client = openai.OpenAI(api_key=api_key)

@app.get('/chatgpt', response_class=HTMLResponse)
async def gpt_page(request: Request):
   return templates.TemplateResponse("gpt.html", {"request": request})

@app.post('/chatgpt', response_class=JSONResponse)
async def chat_with_gpt(
    request: Request,
    message: str = Form(...),
    openai_dependency: OpenAIDependency = Depends()
):
    print(f"Received message: {message}")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        stream = openai_dependency.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
            max_tokens=10  # Ліміт
        )
        generated_message = ""
        async for chunk in stream:
           if chunk.choices[0].delta.content is not None:
              generated_message += chunk.choices[0].delta.content
        print(f"Generated message: {generated_message}")
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
    return {"generated_message": generated_message}

''' Previous snippet yields a response in parallel to ChatGPT`s generation 
    Below snippet yields a response only when it is fully generated by it '''
# @app.post('/chatgpt', response_class=JSONResponse)
# async def chat_with_gpt(
#     request: Request,
#     message: str = Form(...),
#     openai_dependency: OpenAIDependency = Depends()
# ):
#     print(f"Received message: {message}")
#     if not message:
#         raise HTTPException(status_code=400, detail="Message cannot be empty")
#     try:
#         chat_completion = openai_dependency.client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": message}],
#             max_tokens=10 # Ліміт
#         )
#         generated_message = chat_completion.choices[0].message['content']
#         print(f"Generated message: {generated_message}")
#     except Exception as e:
#         print(f"Error generating response: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")
#     return {"generated_message": generated_message}


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

''' Above snippet redirects to external original site that you had created.
    Below one yields a proxy http://127.0.0.1:8000/ComeBackAndAlive/ w/s, but when 
    moving there - instead of e.g. http://127.0.0.1:8000/ComeBackAndAlive/materials, 
    it returns {"error":"Site not found"}, http://127.0.0.1:8000/materials/ '''

# import requests 
# @app.get("/go-to-site/{site_id}")
# async def go_to_site(request: Request, site_id: int):
#   user = request.session.get("user")
#   if not user:
#       return RedirectResponse("/login")
#   site = db.session.query(ModelSite).filter(ModelSite.id == site_id, ModelSite.user_id == user["id"]).first()
#   if site:
#       return RedirectResponse(f"http://127.0.0.1:8000/{site.name}") # Redirect to your site
#   else:
#       return RedirectResponse("/account")

# @app.post("/")
# async def handle_post_request(request: Request):
#    pass
# @app.get("/{site_name}/{path:path}")
# async def redirect_to_site(site_name: str, path: str):
#    site = db.session.query(ModelSite).filter(ModelSite.name == site_name).first()
#    if site:
#        original_site_response = requests.get(f"{site.url}/{path}")
#        original_site_content = original_site_response.text
#        return HTMLResponse(content=original_site_content)
#    else:
#        return {"error": "Site not found"}


''' Next snippets are for Swagger UI http://127.0.0.1:8000/docs#/ '''
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