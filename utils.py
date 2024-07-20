from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from settings import settings
from models import UserInDB

from passlib.context import CryptContext

async def create_user(username: str, email: str, password: str, db):
    hashed_password = get_password_hash(password)
    user_data = {
        "username": username, 
        "email": email,
        "hashed_password": hashed_password,
        "created_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(user_data)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
    

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(db, username: str, password: str):
    user = await db.users.find_one({"username": username})
    if not user:
        return False
    print(f"Hashed password from DB: {user.get('hashed_password')}")  # Debugging line
    if not verify_password(password,user.get("hashed_password", "")):
        return False
    return UserInDB(**user)

