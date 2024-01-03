from pydantic import BaseModel, EmailStr
from enum import Enum

class Status(str,Enum):
    pending = 'pending'
    completed = 'completed'


class TaskBase(BaseModel):
    description: str
    status: Status

    class Config:
        use_enum_values = True
        from_attributes = True
class TaskOut(TaskBase):
    id:int
    user_id:int


class UserBase(BaseModel):
    username:str
    email: EmailStr

    class Config:
        from_attributes = True
class UserRegister(UserBase):
    password:str

class UserOut(UserBase):
    id:int
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
