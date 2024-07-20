from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_database
from bson import ObjectId
from utils import get_password_hash
from datetime import datetime

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db=Depends(get_database)):
    # 이미 존재하는 사용자인지 확인
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # 비밀번호 해싱 (실제 구현시에는 보안을 위해 반드시 해싱해야 함)
    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    user_data["created_at"] = datetime.utcnow()
    result = await db.users.insert_one(user_data)
    
    return {"id": str(result.inserted_id), "username": user.username}

@router.post("/login")
async def login_user(user: UserLogin, db=Depends(get_database)):
    db_user = await db.users.find_one({"username": user.username})
    if not db_user or db_user["password"] != user.password:  # TODO: 실제로는 해싱된 비밀번호를 비교해야 함
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # TODO: JWT 토큰 생성 및 반환
    return {"message": "Login successful"}

@router.get("/me")
async def read_users_me():
    return {"username": "fakecurrentuser"}  # TODO: 실제 인증된 사용자 정보 반환