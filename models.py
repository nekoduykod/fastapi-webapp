from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func 

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String(255))  # 255, if you will do hashing
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    sites = relationship("Site", back_populates="user")
    user_statistics = relationship("Statistics", back_populates="user")

class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    url = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("Users", back_populates="sites")

class Statistics(Base):
    __tablename__ = "statistics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    page_transitions = Column(Integer)
    vpn_site_transitions = Column(Integer)
    data_sent = Column(Integer)
    data_received = Column(Integer)

    user = relationship("Users", back_populates="user_statistics")