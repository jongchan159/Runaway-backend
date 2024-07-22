from fastapi import APIRouter, Depends, HTTPException
from database import get_database
from datetime import datetime, timedelta, timezone
from bson import ObjectId

router = APIRouter()

@router.get("/weekly/{user_id}")
async def get_weekly_stats(user_id: str, db=Depends(get_database)):
    # 오늘 날짜
    today = datetime.now(timezone.utc)
    # 이번 주 월요일 날짜 계산
    start_date = today - timedelta(days=today.weekday())
    start_date = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=1)
    if not result:
        return {"total_distance": 0, "total_duration": 0, "count": 0, "average_pace": 0}
    
    stats = result[0]
    stats["average_pace"] = stats["total_duration"] / stats["total_distance"] if stats["total_distance"] > 0 else 0
    return stats

@router.get("/monthly/{user_id}")
async def get_monthly_stats(user_id: str, db=Depends(get_database)):
    # 오늘 날짜
    today = datetime.now(timezone.utc)
    # 이번 달부터 통계를 계산
    start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=1)
    if not result:
        return {"total_distance": 0, "total_duration": 0, "count": 0, "average_pace": 0}
    
    stats = result[0]
    stats["average_pace"] = stats["total_duration"] / stats["total_distance"] if stats["total_distance"] > 0 else 0
    return stats


@router.get("/yearly/{user_id}")
async def get_yearly_stats(user_id: str, db=Depends(get_database)):
    # 오늘 날짜
    today = datetime.now(timezone.utc)
    # 올해의 1월 1일 날짜
    start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=1)
    if not result:
        return {"total_distance": 0, "total_duration": 0, "count": 0, "average_pace": 0}
    
    stats = result[0]
    stats["average_pace"] = stats["total_duration"] / stats["total_distance"] if stats["total_distance"] > 0 else 0
    return stats


@router.get("/all-time/{user_id}")
async def get_all_time_stats(user_id: str, db=Depends(get_database)):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=1)
    if not result:
        return {"total_distance": 0, "total_duration": 0, "count": 0, "average_pace": 0}
    
    stats = result[0]
    stats["average_pace"] = stats["total_duration"] / stats["total_distance"] if stats["total_distance"] > 0 else 0
    return stats
