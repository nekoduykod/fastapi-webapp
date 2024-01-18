from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import db

from app.models import Shortcuts as ModelShortcuts


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/create-shortcut")
async def create_shortcut(request: Request,
                   shortcut_title: str = Form(...),
                     shortcut_url: str = Form(...)):
  user = request.session.get("user")
  if user:
     site = ModelShortcuts(name=shortcut_title, url=shortcut_url, user_id=user["id"])
     db.session.add(site)
     db.session.commit()
     return RedirectResponse(url="/account", status_code=303)
  else:
     return RedirectResponse("/login")


@router.get("/update-shortcuts")
async def update_shortcuts(request: Request):
 user = request.session.get("user")
 if user:
   user_id = user["id"]
   sites = db.session.query(ModelShortcuts) \
                     .filter(ModelShortcuts.user_id == user_id).all()
   return {"sites": [{"name": site.name, 
                        "id": site.id} 
                          for site in sites]}
 else:
   return {"error": "You are not logged in"}


@router.get("/go-to-shortcut/{site_id}")
async def go_to_shortcut(request: Request,
                         site_id: int):
   user = request.session.get("user")
   if not user:
       return RedirectResponse("/login")
   site = db.session.query(ModelShortcuts) \
                    .filter(ModelShortcuts.id == site_id,
                            ModelShortcuts.user_id == user["id"]).first()
   if site:
       return RedirectResponse(site.url)
   else:
       return RedirectResponse("/account")