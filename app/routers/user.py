from pyexpat import model
from .. import models, schemas, utils, oauth2
from fastapi import Depends, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # checking if user already exists
    user_query = db.query(models.User).filter(models.User.email==user.email)
    if user_query.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail=f"user with email: {user.email} already exist")
    # password hashing
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    # adding user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/getcurrent_user", response_model=schemas.User)
def get_user(db: Session = Depends(get_db),
            current_user: int = Depends(oauth2.get_current_user)):
    return current_user