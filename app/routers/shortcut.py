from fastapi import Request, Form, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_sqlalchemy import db

from app.models.models import Shortcuts as ModelShortcuts


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.post("/create-shortcut")
async def create_shortcut(request: Request,
                   shortcut_title: str = Form(...),
                     shortcut_url: str = Form(...)):
  user = request.session.get("user")
  if user:
     shortcut = ModelShortcuts(title=shortcut_title, url=shortcut_url, user_id=user["id"])
     db.session.add(shortcut)
     db.session.commit()
     return RedirectResponse(url="/account", status_code=303)
  else:
     return RedirectResponse("/account")


@router.delete("/delete-shortcut/{shortcut_id}")
async def delete_shortcut(request: Request, shortcut_id: int):
    user = request.session.get("user")
    if not user:
        return RedirectResponse("/login")

    shortcut = db.session.query(ModelShortcuts).filter(
        ModelShortcuts.id == shortcut_id,
        ModelShortcuts.user_id == user["id"]
    ).first()

    if shortcut:
        db.session.delete(shortcut)
        db.session.commit()
        return {"message": "Shortcut deleted successfully"}
    else:
        return {"error": "Shortcut wasn`t created"}
    

@router.get("/update-shortcuts")
async def update_shortcuts(request: Request):
   user = request.session.get("user")
   if user:
      user_id = user["id"]
      shortcuts = db.session.query(ModelShortcuts) \
                           .filter(ModelShortcuts.user_id == user_id).all()
      return {"shortcuts": [{"title": shortcut.title, 
                               "id": shortcut.id} 
                            for shortcut in shortcuts]}
   else:
      return {"error": "You are not logged in"}


@router.get("/go-to-shortcut/{shortcut_id}")
async def go_to_shortcut(request: Request,
                         shortcut_id: int):
   user = request.session.get("user")
   if not user:
       return RedirectResponse("/login")
   shortcuts = db.session.query(ModelShortcuts) \
                    .filter(ModelShortcuts.id == shortcut_id,
                            ModelShortcuts.user_id == user["id"]).first()
   if shortcuts:
       return RedirectResponse(shortcuts.url)
   else:
       return RedirectResponse("/account")