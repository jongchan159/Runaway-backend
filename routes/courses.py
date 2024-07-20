from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_database
from bson import ObjectId
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder


router = APIRouter()

class CourseCreate(BaseModel):
    name: str
    route: list
    distance: float

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, db=Depends(get_database)):
    course_data = course.dict()
    course_data["created_at"] = datetime.now(timezone.utc)
    result = await db.courses.insert_one(course_data)
    return {"id": str(result.inserted_id), "name": course.name}

@router.get("/recommend")
async def recommend_course(db=Depends(get_database)):
    # 실제 구현에서는 더 복잡한 추천 로직이 필요할 수 있습니다
    course = await db.courses.find_one(sort=[("created_at", -1)])
    if not course:
        raise HTTPException(status_code=404, detail="No courses found")
    return jsonable_encoder(course, custom_encoder={ObjectId: str})

@router.get("/list")
async def list_courses(db=Depends(get_database)):
    cursor = db.courses.find().sort("created_at", -1).limit(10)
    courses = await cursor.to_list(length=10)
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})