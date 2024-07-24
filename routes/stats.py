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
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}}},
        {"$group": {
            "_id": "$week_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$cond": {"if": {"$eq": ["$distance", 0]}, "then": None, "else": {"$divide": ["$duration", "$distance"]}}}}
        }},
        {"$project": {
            "_id": 0,
            "week_start": {"$ifNull": ["$_id", start_date]},
            "distance": "$total_distance",
            "duration": "$total_duration",
            "count": "$count",
            "average_pace": {"$ifNull": ["$average_pace", 0]}
        }}
    ]
    result = await db.runs.aggregate(pipeline).to_list(length=None)
    if not result:
        return Statistics(user_id=ObjectId(user_id), weekly=WeeklyStats(
            week_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    item = result[0]
    weekly_stats = WeeklyStats(
        week_start=item['week_start'],
        distance=item['distance'],
        duration=item['duration'],
        count=item['count'],
        average_pace=item['average_pace']
    )
    
    return Statistics(user_id=ObjectId(user_id), weekly=weekly_stats)

@router.get("/monthly/{user_id}", response_model=Statistics)
async def get_monthly_stats(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}}},
        {"$group": {
            "_id": "$month_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$cond": {"if": {"$eq": ["$distance", 0]}, "then": None, "else": {"$divide": ["$duration", "$distance"]}}}}
        }},
        {"$project": {
            "_id": 0,
            "month_start": {"$ifNull": ["$_id", start_date]},
            "distance": "$total_distance",
            "duration": "$total_duration",
            "count": "$count",
            "average_pace": {"$ifNull": ["$average_pace", 0]}
        }}
    ]
    result = await db.runs.aggregate(pipeline).to_list(length=None)
    if not result:
        return Statistics(user_id=ObjectId(user_id), monthly=MonthlyStats(
            month_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    item = result[0]
    monthly_stats = MonthlyStats(
        month_start=item['month_start'],
        distance=item['distance'],
        duration=item['duration'],
        count=item['count'],
        average_pace=item['average_pace']
    )
    
    return Statistics(user_id=ObjectId(user_id), monthly=monthly_stats)

@router.get("/yearly/{user_id}", response_model=Statistics)
async def get_yearly_stats(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id), "start_time": {"$gte": start_date}}},
        {"$group": {
            "_id": "$year_start",
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$cond": {"if": {"$eq": ["$distance", 0]}, "then": None, "else": {"$divide": ["$duration", "$distance"]}}}}
        }},
        {"$project": {
            "_id": 0,
            "year_start": {"$ifNull": ["$_id", start_date]},
            "distance": "$total_distance",
            "duration": "$total_duration",
            "count": "$count",
            "average_pace": {"$ifNull": ["$average_pace", 0]}
        }}
    ]
    result = await db.runs.aggregate(pipeline).to_list(length=None)
    if not result:
        return Statistics(user_id=ObjectId(user_id), yearly=YearlyStats(
            year_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    item = result[0]
    yearly_stats = YearlyStats(
        year_start=item['year_start'],
        distance=item['distance'],
        duration=item['duration'],
        count=item['count'],
        average_pace=item['average_pace']
    )
    
    return Statistics(user_id=ObjectId(user_id), yearly=yearly_stats)

@router.get("/all_time/{user_id}", response_model=Statistics)
async def get_all_time_stats(user_id: str, db=Depends(get_database)):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {
            "_id": None,
            "total_distance": {"$sum": "$distance"},
            "total_duration": {"$sum": "$duration"},
            "count": {"$sum": 1},
            "average_pace": {"$avg": {"$cond": {"if": {"$eq": ["$distance", 0]}, "then": None, "else": {"$divide": ["$duration", "$distance"]}}}}
        }},
        {"$project": {
            "_id": 0,
            "year_start": {"$ifNull": [datetime.now(timezone.utc), datetime.now(timezone.utc)]},
            "distance": "$total_distance",
            "duration": "$total_duration",
            "count": "$count",
            "average_pace": {"$ifNull": ["$average_pace", 0]}
        }}
    ]
    result = await db.runs.aggregate(pipeline).to_list(length=1)
    if not result:
        return Statistics(user_id=ObjectId(user_id), totally=TotalStats(
            year_start=datetime.now(timezone.utc),
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    stats = result[0]
    total_stats = TotalStats(
        year_start=stats['year_start'],
        distance=stats['distance'],
        duration=stats['duration'],
        count=stats['count'],
        average_pace=stats['average_pace']
    )
    
    return Statistics(user_id=ObjectId(user_id), totally=total_stats)



