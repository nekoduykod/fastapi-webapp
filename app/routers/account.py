from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from app.models import Users as ModelUsers


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get('/account', response_class=HTMLResponse)
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


@router.post('/account', response_class=HTMLResponse)
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