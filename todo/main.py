from fastapi import Depends, FastAPI,APIRouter

#import models
from .middleware import UserAuthenticationMiddleware
from . import  models
from .database import engine

from todo.routers import tasks, users

router = APIRouter()
models.Base.metadata.create_all(bind=engine)
app=FastAPI(docs_url="/docs", redoc_url=None)
app.add_middleware(UserAuthenticationMiddleware)

app.include_router(users.router)
app.include_router(tasks.router)



# if __name__=="__main__":
#     import uvicorn
#     uvicorn.run(
#         "main:app",
#         host="localhost",
#         port=8000,
#         reload=True,
#     )