from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.middleware.setup_middlewares import setup_middlewares
from app.middleware.setup_db import setup_database

from app.routers import main_router


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(main_router)


setup_database(app)
setup_middlewares(app)


@app.get('/', response_class=HTMLResponse)
async def home(request: Request):      
    return templates.TemplateResponse("home.html", {"request": request})