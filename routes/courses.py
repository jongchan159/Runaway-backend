from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from database import get_database
from bson import ObjectId
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from typing import List, Dict, Any, Optional

router = APIRouter()

class CourseCreate(BaseModel):
    name: str
    route: Dict[str, Any]
    distance: float

class Location(BaseModel):
    latitude: float
    longitude: float

# 코스 저장
@router.post("/create_course", status_code=status.HTTP_201_CREATED)
async def create_course(course: CourseCreate, user_id: str = Query(...), db=Depends(get_database)):
    course_data = course.dict()
    course_data["created_by"] = ObjectId(user_id)
    course_data["created_at"] = datetime.now(timezone.utc)
    result = await db.courses.insert_one(course_data)
    return {"id": str(result.inserted_id), "name": course.name}

# 코스 추천 -> 사용자의 현재 위치를 기반으로 모든 코스 반환
@router.post("/recommend")
async def recommend_course(location: Location, db=Depends(get_database)):
    latitude = location.latitude
    longitude = location.longitude

    # 현재 위치 기준으로 모든 코스를 찾기 위한 쿼리
    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "dist.calculated",
                "maxDistance": 5000,  # 5km 이내
                "spherical": True
            }
        },
        {"$sort": {"created_at": -1}}
    ]

    courses = await db.courses.aggregate(pipeline).to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found nearby")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})

# 유저의 모든 코스 리스트
@router.get("/all_courses/{user_id}")
async def all_courses(user_id: str, db=Depends(get_database)):
    cursor = db.courses.find({"created_by": ObjectId(user_id)}).sort("created_at", -1)
    courses = await cursor.to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for the user")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})
