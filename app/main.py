from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .routers import login, register, account, shortcut, chatgpt

import uvicorn

from dotenv import load_dotenv
import os

load_dotenv(".env")


app = FastAPI()
templates = Jinja2Templates(directory="templates")


app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.add_middleware(SessionMiddleware, secret_key="bananabomb")

app.include_router(register.router)
app.include_router(login.router)

app.include_router(account.router)
app.include_router(shortcut.router)
app.include_router(chatgpt.router)


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):      
    return templates.TemplateResponse("home.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)