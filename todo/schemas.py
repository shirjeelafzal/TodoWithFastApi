from pydantic import BaseModel, EmailStr

class TaskBase(BaseModel):
    description: str
    status: str
    user_id:int

    class Config:
        from_attributes = True

class TaskOut(TaskBase):
    id:int


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
