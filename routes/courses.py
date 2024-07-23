from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from database import get_database
from bson import ObjectId
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from typing import List, Dict, Any, Optional
from bson.binary import Binary
from models import Course

router = APIRouter()

class CourseCreate(BaseModel):
    route: bytes
    route_coordinate: Dict[str, Any]
    distance: float

class Location(BaseModel):
    latitude: float
    longitude: float

# 코스 저장
@router.post("/create_course", status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate, 
    user_id: str = Query(...), 
    db=Depends(get_database)
):
    course_data = {
        "route": Binary(course.route),
        "route_coordinate": course.route_coordinate,
        "distance": course.distance,
        "created_by": ObjectId(course.created_by),
        "created_at": datetime.now(timezone.utc),
        "recommendation_count": 0
    }
    result = await db.courses.insert_one(course_data)
    return {"id": str(result.inserted_id)}

# 코스 추천 -> 최신순 정렬
@router.post("/latest")
async def recommend_course_latest(location: Location, db=Depends(get_database)):
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
        {"$sort": {"created_at": -1}} # 최신순 필터
    ]

    courses = await db.courses.aggregate(pipeline).to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found nearby")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})

# 코스 추천 -> 인기순 정렬
@router.post("/recommend", status_code=status.HTTP_200_OK)
async def recommend_course_sorted(location: Location, db=Depends(get_database)):
    latitude = location.latitude
    longitude = location.longitude

    pipeline = [
        {
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [longitude, latitude]},
                "distanceField": "dist.calculated",
                "maxDistance": 5000,  # 5km 이내
                "spherical": True
            }
        },
        {"$sort": {"recommendation_count": -1}} # 인기순 필터
    ]

    courses = await db.courses.aggregate(pipeline).to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found nearby")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})


# 코스 id를 받고 코스 전체를 반환하는 엔드포인트
@router.get("/course/{course_id}", response_model=Course)
async def get_course(course_id: str, db=Depends(get_database)):
    course = await db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return jsonable_encoder(course, custom_encoder={ObjectId: str})

# 유저의 모든 코스 리스트
@router.get("/all_courses/{user_id}")
async def all_courses(user_id: str, db=Depends(get_database)):
    cursor = db.courses.find({"created_by": ObjectId(user_id)}).sort("created_at", -1)
    courses = await cursor.to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for the user")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})
