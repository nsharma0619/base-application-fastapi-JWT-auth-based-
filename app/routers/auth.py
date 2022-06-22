from urllib.parse import uses_relative
from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import database
from app.database import get_db
from google.oauth2 import id_token
from google.auth.transport import requests
from .. import models, schemas, utils, oauth2, config


router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Invalid Credentials")
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Invalid Credentials")
    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token" : access_token, "token_type": "bearer"}
    

@router.post('/google-login/swap-token', response_model=schemas.Token)
def google_login_swap_token(google_token: schemas.GoogleAuthToken = Depends(), db: Session=Depends(database.get_db)):
    try:
        idinfo = id_token.verify_oauth2_token(google_token.auth_token, 
                requests.Request(), config.setting.google_client_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Invalid Credentials")
    user = db.query(models.User).filter(models.User.email == idinfo.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user not found")
    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token" : access_token, "token_type": "bearer"}
    