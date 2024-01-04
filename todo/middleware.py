from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from .oauth2 import get_current_user



class UserAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, db: Session = Depends(get_db)):
        super().__init__(app)
        self.app = app
        self.db = db

    async def dispatch(self, request, call_next):
        
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        if token and token !='Basic Og==':
            user_id = await get_current_user(token)
            request.state.user_id = user_id
        

        response = await call_next(request)
        return response
