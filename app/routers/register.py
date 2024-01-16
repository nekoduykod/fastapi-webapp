from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import db

from app.models import Users as ModelUsers


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get('/register', response_class=HTMLResponse)
async def registr_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
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