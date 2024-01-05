from fastapi import Depends, HTTPException, status,Query,APIRouter,Request
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

router = APIRouter(
    prefix="/tasks",
    
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
@router.post("/", tags=["Tasks"],status_code=status.HTTP_201_CREATED,response_model=schemas.TaskOut)
async def create_task(data: schemas.TaskBase,request:Request,token:Annotated[str, Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    current_user=request.state.user_id
    new_task_data = data.model_dump()
    new_task_data["user_id"] = current_user
    new_task = models.Task(**new_task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=list[schemas.TaskOut])
async def get_all_tasks(request:Request,token:Annotated[str, Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    current_user=request.state.user_id
    tasks = db.query(models.Task).all()
    if tasks and current_user: 
        return tasks
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tasks found")

@router.get("/{id}", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=schemas.TaskOut)
async def get_task(id:int,request:Request,token:Annotated[str, Depends(oauth2_scheme)],db:Session=Depends(get_db)): #,current_user:int=Depends(oauth2.get_current_user)
    task=db.query(models.Task).filter(models.Task.id==id).first()
    current_user=request.state.user_id
    if task:
        if task.user_id==current_user: # type: ignore
            if db.query(models.Task).filter(models.Task.user_id==current_user).first():
                if not task:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
                return task
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No Task present with the id: {id}")

@router.put("/{id}", tags=["Tasks"],status_code=status.HTTP_202_ACCEPTED)
async def update_task(id:int,data: schemas.TaskBase,request:Request,token:Annotated[str, Depends(oauth2_scheme)],db:Session=Depends(get_db)):
    task_to_update = db.query(models.Task).filter(models.Task.id == id).first()
    current_user=request.state.user_id
    if task_to_update:
        if task_to_update.user_id==current_user: # type: ignore
            if db.query(models.Task).filter(models.Task.id==id).first():
                task_data=data.model_dump()
                task_data["user_id"]=current_user
                status_value = task_data.get("status")
                task_data=data.model_dump()
                db.query(models.Task).filter(models.Task.id==id).update(task_data)  # type: ignore
                db.commit()
                return {"detail":"Task Updated Successfully"}
            else:
        
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"You are unauthorized")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No task present with the id: {id}")

@router.delete("/{id}", tags=["Tasks"], status_code=status.HTTP_200_OK)
async def delete_task(id: int,request:Request,token:Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    task_to_delete = db.query(models.Task).filter(models.Task.id == id).first()
    current_user=request.state.user_id
    if task_to_delete and current_user:
        if task_to_delete.user_id == current_user: # type: ignore
            db.query(models.Task).filter(models.Task.id == id).delete(synchronize_session=False)
            db.commit()
            return {"detail": "Task has been deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are unauthorized")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No task present with the id: {id}")

