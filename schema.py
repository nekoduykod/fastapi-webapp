from pydantic import BaseModel

class Users(BaseModel):
    username: str    
    password: str
    email: str   

    class Config:
        orm_mode = True 

class Statistics(BaseModel):
    id: int   
    user_id: int   
    page_transitions: int 
    vpn_site_transitions: int
    data_sent: int
    data_received: int
    
    class Config:
        orm_mode = True
