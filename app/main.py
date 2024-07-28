from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .routers import login, register, account, shortcut, chatgpt
from config import SQLITE_URL, SESSION_MIDDL_SECRET_KEY


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(DBSessionMiddleware, db_url=SQLITE_URL)
app.add_middleware(SessionMiddleware, secret_key=SESSION_MIDDL_SECRET_KEY)

app.include_router(register.router)
app.include_router(login.router)
app.include_router(account.router)
app.include_router(shortcut.router)
app.include_router(chatgpt.router)


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):      
    return templates.TemplateResponse("home.html", {"request": request})