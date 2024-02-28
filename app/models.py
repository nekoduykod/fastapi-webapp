from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
<<<<<<< HEAD
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from passlib.context import CryptContext
=======
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
>>>>>>> parent of 1746764 (Merge branch 'main' of https://github.com/nekoduykod/webapp_with_openai)


Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String(255))
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shortcuts = relationship("Shortcuts", back_populates="users")

class Shortcuts(Base):
    __tablename__ = "shortcuts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    users = relationship("Users", back_populates="shortcuts", foreign_keys=[user_id])