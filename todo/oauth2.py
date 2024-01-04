from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from . import JWTtoken,schemas
from typing import Annotated
from jose import  jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)])->int: # type: ignore
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = jwt.decode(token, JWTtoken.SECRET_KEY, algorithms=[JWTtoken.ALGORITHM]) # type: ignore
    print(payload)
    username: str = payload.get("sub") # type: ignore
    user_id:int=payload.get("user_id") # type: ignore
    if username is None or user_id is None:
        raise credentials_exception
    token_data = schemas.TokenData(username=username)

    return user_id
    