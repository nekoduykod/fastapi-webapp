from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from app.models import Users as ModelUsers


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
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
      request.session["error"] = "Invalid login or password"
      return templates.TemplateResponse("login.html",
                                       {"request": request,
                                          "error": request.session.get('error')})