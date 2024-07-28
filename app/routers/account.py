from fastapi import Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from passlib.context import CryptContext

from app.models.models import Users as ModelUsers
from app.models.models import Shortcuts as ModelShortcuts


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get('/account', response_class=HTMLResponse)
async def account_page(request: Request):
    user = request.session.get("user")
    if user:
       shortcuts = db.session.query(ModelShortcuts).filter_by(user_id=user["id"]).all()
       return templates.TemplateResponse("account.html", 
                                        {"request": request,
                                            "user": user,
                                            "shortcuts": shortcuts,
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
    username = request.session.get("user")["username"]
    existing_user = db.session.query(ModelUsers) \
                              .filter(ModelUsers.username == username).first()

    if not existing_user or not pwd_context.verify(current_password, existing_user.hashed_password):
        return templates.TemplateResponse("account.html",
                                    {"request": request,
                                        "user": {"username": username, "email": existing_user.email},
                                       "error": "Incorrect current password"})
    if new_password != confirm_password:
        return templates.TemplateResponse("account.html",
                                    {"request": request,
                                        "user": {"username": username, "email": existing_user.email},
                                       "error": "New and confirm password do not match"})
    existing_user.set_password(new_password)
    db.session.commit()

    request.session["user"] = {"username": username,
                                  "email": existing_user.email,
                                     "id": existing_user.id}
    
    return templates.TemplateResponse("account.html",
                                {"request": request,
                                    "user": request.session["user"],
                                 "success": "Password changed successfully"})


@router.post('/delete-shortcut/{shortcut_id}', response_class=HTMLResponse)
async def delete_shortcut(request: Request, shortcut_id: int):
    user = request.session.get("user")
    if not user:
        return templates.TemplateResponse("account.html",
                                          {"request": request, "user": None, "error": "You are not logged in"})

    shortcut = db.session.query(ModelShortcuts).filter_by(id=shortcut_id, user_id=user["id"]).first()
    if not shortcut:
        return templates.TemplateResponse("account.html",
                                          {"request": request, "user": user, "error": "Shortcut not found"})

    db.session.delete(shortcut)
    db.session.commit()

    updated_shortcuts = db.session.query(ModelShortcuts).filter_by(user_id=user["id"]).all()
    return templates.TemplateResponse("account.html",
                                      {"request": request, "user": user, "shortcuts": updated_shortcuts, "success": "Shortcut deleted successfully"})
