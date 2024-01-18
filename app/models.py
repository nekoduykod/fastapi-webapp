from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


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