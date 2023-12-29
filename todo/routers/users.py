        
from fastapi import Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from .. import  JWTtoken, models, schemas, hashed_password,oauth2
from ..database import get_db
from datetime import  timedelta
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users",
)


@router.post("/login",tags=["Authentication"])
async def login(request:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.username==request.username).first()
    if not user:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Username")
    is_valid_password=hashed_password.verify_password(request.password,user.password)
    if not is_valid_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Invalid Password")
    access_token_expires = timedelta(minutes=JWTtoken.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWTtoken.create_access_token(
        data={"sub": user.username,"user_id":user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register",tags=["Users"],response_model=schemas.UserBase,status_code=status.HTTP_201_CREATED)
async def register(request:schemas.UserRegister,db:Session=Depends(get_db)):
    hashed_pswd=hashed_password.get_password_hash(request.password)
    new_user_data=request.model_dump()
    new_user_data["password"]= hashed_pswd
    new_user=models.User(**new_user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/",tags=["Users"],response_model=list[schemas.UserOut],status_code=status.HTTP_200_OK)
async def get_all_users(db:Session=Depends(get_db)):#,current_user:schemas.UserBase=Depends(oauth2.get_current_user)
   if db.query(models.User).all():
       return db.query(models.User).all()
   else:
       raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,detail="No user is present")

@router.get("/{id}",tags=["Users"],response_model=list[schemas.UserOut],status_code=status.HTTP_200_OK)
async def get_users(id:int,db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
   if db.query(models.User).filter(models.User.id==id).first():
       return db.query(models.User).filter(models.User.id==id).first()
   else:
       raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")

@router.put("/{id}",tags=["Users"],status_code=status.HTTP_200_OK)
async def update_users(id:int,request:schemas.UserBase,db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    user= db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
   
    user_data=request.model_dump()
    db.query(models.User).filter(models.User.id==id).update(user_data) # type: ignore
    db.commit()
    return {"detail":"User has been updated successfully"}

@router.delete("/{id}",tags=["Users"],status_code=status.HTTP_200_OK)
async def delete_users(id:int,db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    user= db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException (status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
   
    db.query(models.User).filter(models.User.id==id).delete(synchronize_session=False)
    db.commit()
    return {"detail":"User has been deleted successfully"}

       



