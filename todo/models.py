from .database import Base
from sqlalchemy import  Column, ForeignKey, Integer, String,JSON
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username=Column(String, index=True,unique=True)
    email = Column(String, index=True,unique=True)
    password = Column(String)

    tasks = relationship("Task", back_populates="creator")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    description = Column(String, index=True)
    status = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    creator= relationship("User", back_populates="tasks")
    
    
class Log_data(Base):
    __tablename__ = 'log_data'

    id = Column(Integer, primary_key=True, index=True)
    request_method = Column(String)
    request_headers = Column(JSON)  # Change this to JSON or another suitable type
    request_url = Column(String)
    response_status_code = Column(Integer)
    response_headers = Column(JSON)  # Change this to JSON or another suitable type
