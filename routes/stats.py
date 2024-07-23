from fastapi import APIRouter, Depends, HTTPException
from database import get_database
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from models import Statistics, WeeklyStats, MonthlyStats, YearlyStats, TotalStats

router = APIRouter()


@router.get("/weekly/{user_id}", response_model=Statistics)
async def get_weekly_stats(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=today.weekday())
    start_date = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": "$week_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$divide": ["$duration", "$distance"]}}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=None)
    if not result:
        return {"weekly": []}
    
    weekly_stats = [WeeklyStats(
        week_start=item['_id'],
        distance=item['total_distance'],
        duration=item['total_duration'],
        count=item['count'],
        average_pace=item['average_pace']
    ) for item in result]
    
    return {"weekly": weekly_stats}

@router.get("/monthly/{user_id}", response_model=Statistics)
async def get_monthly_stats(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": "$month_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$divide": ["$duration", "$distance"]}}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=None)
    if not result:
        return {"monthly": []}
    
    monthly_stats = [MonthlyStats(
        month_start=item['_id'],
        distance=item['total_distance'],
        duration=item['total_duration'],
        count=item['count'],
        average_pace=item['average_pace']
    ) for item in result]
    
    return {"monthly": monthly_stats}

@router.get("/yearly/{user_id}", response_model=Statistics)
async def get_yearly_stats(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}, "status": "completed"}},
        {"$group": {
            "_id": "$year_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$divide": ["$duration", "$distance"]}}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=None)
    if not result:
        return {"yearly": []}
    
    yearly_stats = [YearlyStats(
        year_start=item['_id'],
        distance=item['total_distance'],
        duration=item['total_duration'],
        count=item['count'],
        average_pace=item['average_pace']
    ) for item in result]
    
    return {"yearly": yearly_stats}

@router.get("/all_time/{user_id}", response_model=Statistics)
async def get_all_time_stats(user_id: str, db=Depends(get_database)):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "status": "completed"}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$divide": ["$duration", "$distance"]}}
        }}
    ]
    result = await db.running_sessions.aggregate(pipeline).to_list(length=1)
    if not result:
        return {"total_distance": TotalStats(
            year_start=datetime.now(timezone.utc),
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        )}
    
    stats = result[0]
    total_distance = TotalStats(
        year_start=datetime.now(timezone.utc),
        distance=stats['total_distance'],
        duration=stats['total_duration'],
        count=stats['count'],
        average_pace=stats['average_pace']
    )
    
    return {"total_distance": total_distance}

