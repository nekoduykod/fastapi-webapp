from fastapi_sqlalchemy import DBSessionMiddleware
from app.config import SQLITE_URL


def setup_database(app):
    app.add_middleware(DBSessionMiddleware, db_url=SQLITE_URL)