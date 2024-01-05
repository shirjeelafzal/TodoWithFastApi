from fastapi import Depends, Request
from sqlalchemy.orm import Session
from .database import get_db,SessionLocal
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from .oauth2 import get_current_user
import logging
from fastapi.responses import JSONResponse
import logging.config
import logging.config
from .models import Log_data

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

log_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'mode': 'w',  # Set the file mode to 'w' (write)
            'level': 'DEBUG',
            'formatter': 'simple',  # You might want to add a formatter
        },
    },
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

class UserAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        if token and token !='Basic Og==':
            user_id = await get_current_user(token)
            request.state.user_id = user_id

        response = await call_next(request)
        return response
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        try:
            # Log the start of the request
            logger.info(f"Received request: {request.method} {request.url}")
            logger.debug(f"Request Headers: {request.headers}")
            # Continue processing the request
            response = await call_next(request)

            # Log response details (status code, headers, body, etc.)
            logger.debug(f"Response Status Code: {response.status_code}")
            logger.debug(f"Response Headers: {response.headers}")
            
            logger.debug(f"Response Headers: {response.__dict__}")
            
            log_entry = Log_data(
                request_method=request.method,
                request_headers=dict(request.headers),
                request_url=str(request.url),
                response_status_code=response.status_code,
                response_headers=dict(response.headers)
            )
    # Saving the log to the database
            with SessionLocal() as session:
                session.add(log_entry)
                session.commit()
            return response
        except Exception as e:
            print(f"Error processing request: {str(e)}")
            # Log any exceptions that occurred during request processing
            logger.error(f"Error processing request: {str(e)}")
            return JSONResponse(content={"error": "Internal Server Error"}, status_code=500)
