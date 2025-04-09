import dependencies
from fastapi import HTTPException, APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from datetime import timedelta, datetime

from lib import account_number as acc
from lib.account_number import UserInfo
from lib import database as my_db
from lib import smtp, app_token
from config import settings

SEND_GMAIL_MESSAGE_FROMAT = lambda code: f"<h2>驗證碼: {code}</h2>"

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter()

@router.post("/register")
async def register_user(user: acc.AccountNumberCreate, db=Depends(dependencies.get_db)):
    authenticate_code = acc.AuthenticateCode.generate_digit_code(6)
    hashed_authenticate_code = acc.AuthenticateCode.hash(authenticate_code)
    hashed_password = acc.Password.hash(user.password) 

    result = my_db.fetch_one(db, "user_info", "email", user.email)
    
    if result:
        user = UserInfo(result)
        if user.authenticate_status: #信箱已經認證
            raise HTTPException(status_code=400, detail="Email already registered")
        else:
            my_db.delete_one(db, "user_info", "email", user.email)

    try:
        my_db.write(
            db,
            table_name="user_info",
            columns=("email", "hashed_password", "level", "hashed_authenticate_code", "authenticate_status", "today_api_use"),
            data=(user.email, hashed_password, 1, hashed_authenticate_code, False, 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
    smtp.send_gmail(user.email, "Stock Viewer 信箱驗證", SEND_GMAIL_MESSAGE_FROMAT(authenticate_code))

    return {"message": "Verification email has been sent", "email": user.email}

@router.post("/authenticate")
async def register_user(authenticate_user: acc.AccountNumberAuthenticate, db=Depends(dependencies.get_db)):
    result = my_db.fetch_one(db, "user_info", "email", authenticate_user.email)
    user = UserInfo(result)

    if not acc.AuthenticateCode.verify(authenticate_user.authenticate_code, user.hashed_authenticate_code):
        raise HTTPException(status_code=400, detail="Authenticate code error")
    
    current_time = datetime.now()
    if current_time > user.created_at + timedelta(minutes=3):
        raise HTTPException(status_code=400, detail="Authenticate code expired")
    
    try:
        my_db.update_authenticate_status(db, user.email, True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

    return {"message": "Authenticate Successfully", "email": user.email}

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(dependencies.get_db)
) -> Token:
    
    user = acc.AccountNumber.authenticate(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.backend_access_token_expire_minutes)
    access_token = app_token.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")

@router.post("/logout")
async def logout_user(token: Annotated[str, Depends(app_token.oauth2_scheme)]):
    app_token.add_token_to_blacklist(token)
    return {"message": "logout successfully"}

@router.post("/me")
async def user_me(user : Annotated[UserInfo, Depends(dependencies.check_user_info)]):
    return user

@router.post("/list")
async def user_me(user: Annotated[UserInfo, Depends(dependencies.check_admin)]):
    return my_db.get_all_user_info()
