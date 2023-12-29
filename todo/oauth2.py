from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from .import JWTtoken,schemas,models
from typing import Annotated
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]): # type: ignore
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWTtoken.SECRET_KEY, algorithms=[JWTtoken.ALGORITHM]) # type: ignore
        username: str = payload.get("sub") # type: ignore
        user_id:int=payload.get("user_id") # type: ignore
        if username is None or user_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return user_id
    


async def get_current_active_user(current_user: Annotated[models.User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
