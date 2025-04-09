import dependencies
import logging
from fastapi import HTTPException, APIRouter, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Annotated
from datetime import timedelta, datetime

from lib import account_number as acc
from lib.account_number import UserInfo
from lib import database as my_db
from lib import smtp, app_token
from lib.stock import StockInfo, StockHistoryData
from config import settings, UpdateStatusEnum

router = APIRouter()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UpdateDataDate(BaseModel):
    year: int
    month: int

def _update_stock_info_in_background():
    settings.backend_update_info_status = UpdateStatusEnum.updating
    settings.backend_update_info_start_time = datetime.now()

    dict1 = StockInfo.request("上市")
    dict2 = StockInfo.request("上櫃")

    if not dict1 or not dict2:
        settings.update_info_status = UpdateStatusEnum.failed
        return

    combined_dict = {**dict1, **dict2}

    try:
        StockInfo.update_to_db(combined_dict)
        settings.backend_update_info_status = UpdateStatusEnum.completed
        settings.backend_update_info_complete_time = datetime.now()
        logging.info("update stock info finished.")
    except Exception as e:
        settings.backend_update_info_status = UpdateStatusEnum.failed
        logging.error(f"Error updating stock info: {e}", exc_info=True)

def _update_stock_data_in_background(date_str):
    settings.backend_update_data_status = UpdateStatusEnum.updating
    StockHistoryData.update_month(date_str)
    settings.backend_update_data_status = UpdateStatusEnum.completed

@router.get("/stock/info")
async def get_stock_info(user: Annotated[UserInfo, Depends(dependencies.check_admin)]):
    return StockInfo.read()
    
@router.post("/stock/info/update")
async def stock_info_update(user: Annotated[UserInfo, Depends(dependencies.check_admin)], background_tasks: BackgroundTasks):
    background_tasks.add_task(_update_stock_info_in_background)
    return {"message": "Stock information update is processing in the background."}

@router.post("/stock/data/update")
async def stock_data_update(date: UpdateDataDate, user: Annotated[UserInfo, Depends(dependencies.check_admin)], background_tasks: BackgroundTasks):
    date_str = f"{date.year}{date.month:02d}"
    logging.info(f"update stock date {date_str}")
    background_tasks.add_task(_update_stock_data_in_background, date_str)
    return {"message": "Stock data update is processing in the background."}

@router.get("/stock/update/status")
async def stock_update_status(user: Annotated[UserInfo, Depends(dependencies.check_admin)]):
    return {"update_info": {
                "status": settings.backend_update_info_status,
                "start_time": settings.backend_update_info_start_time,
                "complete_time": settings.backend_update_info_complete_time
            },
            "update_data": {
                "status": settings.backend_update_data_status,
                "start_time": settings.backend_update_data_start_time,
                "complete_time": settings.backend_update_data_complete_time
            }}
