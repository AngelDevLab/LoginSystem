from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
import redis

from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

redis_client = redis.StrictRedis(
    host=settings.redis_host,
    port=settings.redis_port, 
    password=settings.redis_password, 
    db=0, 
    decode_responses=True
)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.backend_secret_key, algorithm=settings.backend_algorithm)
    return encoded_jwt

def decode_access_token(token: str):
    return jwt.decode(token, settings.backend_secret_key, algorithms=[settings.backend_algorithm])

def add_token_to_blacklist(token: str):
    redis_client.set(f"blacklisted_token:{token}", "true", ex=(settings.backend_black_list_token_expire_minutes*60))  # 設置過期時間，例如 1 小時

def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklisted_token:{token}")
