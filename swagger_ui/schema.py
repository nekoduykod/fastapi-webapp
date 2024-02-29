from pydantic import BaseModel


class Users(BaseModel):
    username: str    
    password: str
    email: str   

    class Config:
        orm_mode = True 

class Site(BaseModel):
    name: str
    url: str

    class Config:
       orm_mode = True