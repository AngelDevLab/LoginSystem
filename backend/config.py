from pydantic_settings import BaseSettings
from enum import Enum
from typing import Optional
from datetime import datetime

class UpdateStatusEnum(str, Enum):
    idle = "idle"
    updating = "updating"
    completed = "completed"
    failed = "failed"

class Settings(BaseSettings):
    mysql_username: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_database: str

    redis_host: str
    redis_port: int
    redis_password: str

    backend_api_use_count: int
    backend_access_token_expire_minutes: int
    backend_black_list_token_expire_minutes: int
    backend_secret_key: str
    backend_algorithm: str
    
    smtp_gmail: str
    smtp_gmail_password: str

    backend_update_info_status: UpdateStatusEnum = UpdateStatusEnum.idle
    backend_update_info_start_time: Optional[datetime] = None
    backend_update_info_complete_time: Optional[datetime] = None

    backend_update_data_status: UpdateStatusEnum = UpdateStatusEnum.idle
    backend_update_data_start_time: Optional[datetime] = None
    backend_update_data_complete_time: Optional[datetime] = None

    class Config:
        env_file = ".env"

settings = Settings()
