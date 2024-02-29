''' Swagger UI => http://127.0.0.1:8000/docs#/ '''
from fastapi_sqlalchemy import db
from fastapi import FastAPI

import uvicorn

from app.models.models import Users as ModelUsers
from swagger_ui.schema import Users as SchemaUsers


app = FastAPI()


@app.post("/add-user/", response_model=SchemaUsers)
def add_user(user: SchemaUsers):
    db_user = ModelUsers(username=user.username, password=user.password, email=user.email)
    db.session.add(db_user)
    db.session.commit()
    return db_user


@app.get("/users/")
def get_users():
    users = db.session.query(ModelUsers).all()
    return users


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)