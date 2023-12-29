
from fastapi import Depends, HTTPException, status,Query,APIRouter
from sqlalchemy.orm import Session
from .. import  models, schemas, oauth2
from ..database import SessionLocal, engine,get_db

router = APIRouter(
    prefix="/tasks",
)

@router.get("/", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=list[schemas.TaskOut])
async def get_all_task(db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    tasks = db.query(models.Task).all()
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tasks found")
    
    return tasks
    

@router.get("/{id}", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=schemas.TaskOut)
async def get_task(id:int,db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    task=db.query(models.Task).filter(models.Task.id==id).first()
    if db.query(models.Task).filter(models.Task.user_id==current_user).first():
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
        return task
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
@router.post("/", tags=["Tasks"],status_code=status.HTTP_201_CREATED,response_model=schemas.TaskOut)
async def create_task(request: schemas.TaskBase, db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    new_task_data = request.model_dump()#dict() is deprecated ,both of them are doing the same thing
    user_id=new_task_data["user_id"]
    if not db.query(models.User).filter(models.User.id==user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No User present with the id: {user_id}")
    new_task=models.Task(**new_task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task



@router.put("/{id}", tags=["Tasks"],status_code=status.HTTP_202_ACCEPTED)
async def update_task(id:int,request: schemas.TaskBase, db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    if db.query(models.Task).filter(models.Task.user_id==current_user).first():
        if db.query(models.Task).filter(models.Task.id==id).first():
            task_data=request.model_dump(exclude_unset=True)
            db.query(models.Task).filter(models.Task.id==id).update(task_data)  # type: ignore
            db.commit()
            return {"detail":"Task Updated Successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
@router.delete("/{id}", tags=["Tasks"],status_code=status.HTTP_200_OK)
async def delete_task(id:int, db:Session=Depends(get_db),current_user:schemas.UserBase=Depends(oauth2.get_current_user)):
    if db.query(models.Task).filter(models.Task.user_id==current_user).first():
        if db.query(models.Task).filter(models.Task.id==id).first():
            db.query(models.Task).filter(models.Task.id==id).delete(synchronize_session=False)
            db.commit()
            return {"detail":"Task has been deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
        
