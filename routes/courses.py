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
    route: bytes # 코스 이미지
    route_coordinate: Dict[str, Any] # 코스의 좌표리스트
    distance: float # 거리
    course_type: Optional[int] # 0이면 그림, 1이면 추천

class Location(BaseModel):
    latitude: float
    longitude: float

# 코스 저장
@router.post("/create_course/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    user_id: str,
    db=Depends(get_database)
):
    course_data = {
        "route": Binary(course.route),
        "route_coordinate": course.route_coordinate,
        "distance": course.distance,
        "created_by": ObjectId(user_id),  # user_id를 ObjectId로 변환하여 created_by에 저장
        "created_at": datetime.now(timezone.utc),
        "course_type": course.course_type,
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
                "maxDistance": 500000000,  # 5000km 이내
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
@router.get("/{course_id}", response_model=Course)
async def get_course(course_id: str, db=Depends(get_database)):
    course = await db.courses.find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return jsonable_encoder(course, custom_encoder={ObjectId: str})


# user_id와 course_type이 일치하는 코스의 개수 반환
@router.get("/count/{user_id}/{course_type}", response_model=int)
async def count_courses(user_id: str, course_type: int, db=Depends(get_database)):
    count = await db.courses.count_documents({"created_by": ObjectId(user_id), "course_type": course_type})
    return count


# 유저의 모든 코스 리스트
@router.get("/all_courses/{user_id}")
async def all_courses(user_id: str, db=Depends(get_database)):
    cursor = db.courses.find({"created_by": ObjectId(user_id)}).sort("created_at", -1)
    courses = await cursor.to_list(length=None)
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found for the user")
    return jsonable_encoder(courses, custom_encoder={ObjectId: str})
