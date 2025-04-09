from fastapi import Body, HTTPException, Depends, status
from typing import Generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError

from config import settings, UpdateStatusEnum
from lib import database as my_db
from lib import app_token
from lib import account_number as acc
from lib.account_number import UserInfo

def get_db() -> Generator:
    connection = my_db.connection()
    try:
        yield connection
    finally:
        connection.close()

class TokenData(BaseModel):
    username: str | None = None

async def check_user_info(token: Annotated[str, Depends(app_token.oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if app_token.is_token_blacklisted(token):
        raise credentials_exception
    
    try:
        payload = app_token.decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_data = TokenData(username=username)

    except InvalidTokenError:
        raise credentials_exception
    
    #username is email
    db = my_db.connection()
    result = my_db.fetch_one(db, "user_info", "email", token_data.username)
    user = UserInfo(result)
    user_basic_info = user.to_basic_info()

    if user_basic_info is None:
        raise credentials_exception
    
    if user_basic_info.today_api_use >= settings.backend_api_use_count and user_basic_info.level != -1:
        raise HTTPException(status_code=401, detail="API usage limit exceeded, token is blacklisted")
    
    #檢查更新狀態
    if settings.backend_update_info_status == UpdateStatusEnum.updating or settings.backend_update_data_status == UpdateStatusEnum.updating:
        raise HTTPException(status_code=500, detail="Server busy")

    return user_basic_info

async def check_admin(user : Annotated[UserInfo, Depends(check_user_info)]):
    if user.level != -1:
        raise HTTPException(status_code=500, detail="Server response error")
    return user
    