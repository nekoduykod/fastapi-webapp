from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import DBSessionMiddleware, db
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
import os

import openai
from openai import OpenAI

from models import Users as ModelUsers
from models import Site as ModelSite

import uvicorn

load_dotenv("../.env")

app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.add_middleware(SessionMiddleware, secret_key="bananabomb")

client = OpenAI()

templates = Jinja2Templates(directory="../templates")


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):      
    return templates.TemplateResponse("home.html", {"request": request})


@app.get('/register', response_class=HTMLResponse)
async def registr_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, 
                  username: str = Form(...),
                  password: str = Form(...),
                     email: str = Form(...)):
    
    existing_user = db.session.query(ModelUsers) \
                             .filter(ModelUsers.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html",
                                          {"request": request, 
                                             "error": "Username already exists"})
    
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
  
  existing_user = db.session.query(ModelUsers) \
                           .filter(ModelUsers.username == username,
                                   ModelUsers.password == password).first()

  if existing_user:
      request.session["user"] = {"username": username,
                                    "email": existing_user.email,
                                       "id": existing_user.id}
      response = RedirectResponse(url="/account", status_code=303)
      return response
  else:
      return templates.TemplateResponse("login.html", 
                                       {"request": request, 
                                          "error": "Invalid username or password"})


@app.get('/account', response_class=HTMLResponse)
async def account_page(request: Request):
  user = request.session.get("user")
  if user:
      return templates.TemplateResponse("account.html", 
                                        {"request": request,
                                            "user": user, 
                                           "error": None})
  else:
      return templates.TemplateResponse("account.html",
                                        {"request": request,
                                            "user": None, 
                                           "error": "You are not logged in"})

@app.post('/account', response_class=HTMLResponse)
async def change_pass(request: Request,
             current_password: str = Form(...),
                 new_password: str = Form(...),
             confirm_password: str = Form(...)):
 
 user = {"username": request.session.get("user")["username"], 
         "password": current_password}
 existing_user = db.session.query(ModelUsers) \
                          .filter(ModelUsers.username == user["username"], 
                                  ModelUsers.password == user["password"]).first()

 if not existing_user:
    request.session["error"] = "Incorrect current password"
    return templates.TemplateResponse("account.html", 
                                      {"request": request, 
                                          "user": user, 
                                         "error": request.session.get('error')})
 if new_password != confirm_password:
    request.session["error"] = "New password and confirm password do not match"
    return templates.TemplateResponse("account.html", 
                                      {"request": request, 
                                          "user": user, 
                                         "error": request.session.get('error')})
 else:
    existing_user.password = new_password
    db.session.commit() 
    request.session["error"] = "Password changed successfully"
    return templates.TemplateResponse("account.html", 
                                     {"request": request, 
                                         "user": user, 
                                        "error": request.session.get('error')})


def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "not-set-api-key")

class OpenAIDependency:
   def __init__(self, api_key: str = Depends(get_openai_api_key)):
      self.client = openai.OpenAI(api_key=api_key)


@app.get('/chatgpt', response_class=HTMLResponse)
async def gpt_page(request: Request):
   return templates.TemplateResponse("gpt.html", {"request": request})

@app.post('/chatgpt', response_class=JSONResponse)
async def chat_with_gpt(request: Request,
                        message: str = Form(...),
              openai_dependency: OpenAIDependency = Depends()):

    print(f"Received message: {message}")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        stream = openai_dependency.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}],
            stream=True,
            max_tokens=10) # Ліміт
        
        generated_message = ""
        async for chunk in stream:
           if chunk.choices[0].delta.content is not None:
              generated_message += chunk.choices[0].delta.content
        print(f"Generated message: {generated_message}")

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Error generating response: {str(e)}")
    return {"generated_message": generated_message}


@app.post("/create_site")
async def create_site(request: Request, 
                    site_name: str = Form(...),
                     site_url: str = Form(...)):
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
   sites = db.session.query(ModelSite) \
                     .filter(ModelSite.user_id == user_id).all()
   return {"sites": [{"name": site.name, "id": site.id} for site in sites]}
 else:
   return {"error": "You are not logged in"}


@app.get("/go-to-site/{site_id}")
async def go_to_site(request: Request, 
                     site_id: int):
   user = request.session.get("user")
   if not user:
       return RedirectResponse("/login")
   site = db.session.query(ModelSite) \
                    .filter(ModelSite.id == site_id, 
                            ModelSite.user_id == user["id"]).first()
   if site:
       return RedirectResponse(site.url)
   else:
       return RedirectResponse("/account")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)