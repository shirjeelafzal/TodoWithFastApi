from fastapi import Depends, HTTPException, status,Query,APIRouter
from sqlalchemy.orm import Session
from .. import  models, schemas, oauth2
from ..database import SessionLocal, engine,get_db

router = APIRouter(
    prefix="/tasks",
)
@router.post("/", tags=["Tasks"],status_code=status.HTTP_201_CREATED,response_model=schemas.TaskOut)
async def create_task(request: schemas.TaskBase, db:Session=Depends(get_db)):
    new_task_data = request.model_dump()#dict() is deprecated ,both of them are doing the same thing
    user_id=new_task_data["user_id"]
    if not db.query(models.User).filter(models.User.id==user_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No User present with the id: {user_id}")
    if user_id==0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Id cannot be null")
    status_value = new_task_data["status"]
    valid_statuses = ["pending", "completed"]
    if status_value not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status value. Valid values are: {valid_statuses}")

    new_task=models.Task(**new_task_data)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task
@router.get("/", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=list[schemas.TaskOut])
async def get_all_task(db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.user_id==current_user).all()
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tasks found with id {current_user}")
    return tasks

@router.get("/{id}", tags=["Tasks"],status_code=status.HTTP_200_OK,response_model=schemas.TaskOut)
async def get_task(id:int,db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    task=db.query(models.Task).filter(models.Task.id==id).first()
    if task:
        if task.user_id==current_user:
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
async def update_task(id:int,request: schemas.TaskBase, db:Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    task_to_update = db.query(models.Task).filter(models.Task.id == id).first()
    if task_to_update:
        if task_to_update.user_id==current_user:
            if db.query(models.Task).filter(models.Task.id==id).first():
                task_data=request.model_dump()
                if not db.query(models.User).filter(models.User.id==task_data['user_id']).first():
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No User present with the id: {task_data['user_id']}")
                if task_data['user_id']==0:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User Id cannot be null")
                status_value = task_data.get("status")
                task_data=request.model_dump()
                status_value = task_data.get("status")
                valid_statuses = ["pending", "completed"]
                if status_value is not None and status_value not in valid_statuses:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status value. Valid values are: {valid_statuses}")

                valid_statuses = ["pending", "completed"]
                if status_value is not None and status_value not in valid_statuses:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status value. Valid values are: {valid_statuses}")

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
async def delete_task(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    task_to_delete = db.query(models.Task).filter(models.Task.id == id).first()
    if task_to_delete and current_user:
        if task_to_delete.user_id == current_user: # type: ignore
            db.query(models.Task).filter(models.Task.id == id).delete(synchronize_session=False)
            db.commit()
            return {"detail": "Task has been deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are unauthorized")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No task present with the id: {id}")

