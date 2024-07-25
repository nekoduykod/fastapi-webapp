from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from passlib.context import CryptContext


Base = declarative_base()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String(255))
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    # if POSTGRESQL use:
    # created_at = Column(DateTime(timezone=True), server_default=func.now())
    # updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    shortcuts = relationship("Shortcuts", back_populates="users")

    def verify_password(self, password):
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password):
        self.hashed_password = pwd_context.hash(password)


class Shortcuts(Base):
    __tablename__ = "shortcuts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    users = relationship("Users", back_populates="shortcuts", foreign_keys=[user_id])