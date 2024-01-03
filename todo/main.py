from fastapi import Depends, FastAPI,APIRouter
from . import  models
from .database import  engine

from todo.routers import tasks,users

router = APIRouter()

models.Base.metadata.create_all(bind=engine)
app=FastAPI(docs_url="/docs", redoc_url=None)

app.include_router(users.router)
app.include_router(tasks.router)



