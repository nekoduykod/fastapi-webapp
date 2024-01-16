from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi_sqlalchemy import db

from app.models import Site as ModelSite


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.post("/create_site")
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

@router.get("/update_sites")
async def update_sites(request: Request):
 user = request.session.get("user")
 if user:
   user_id = user["id"]
   sites = db.session.query(ModelSite) \
                     .filter(ModelSite.user_id == user_id).all()
   return {"sites": [{"name": site.name, "id": site.id} for site in sites]}
 else:
   return {"error": "You are not logged in"}


@router.get("/go-to-site/{site_id}")
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