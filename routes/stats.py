from fastapi import APIRouter, Depends, HTTPException
from database import get_database
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from models import Statistics, WeeklyStats, MonthlyStats, YearlyStats, TotalStats

router = APIRouter()

@router.get("/weekly/{user_id}", response_model=Statistics)
async def get_weekly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=today.weekday())
    start_date = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    if not statistics or "weekly" not in statistics:
        return Statistics(user_id=ObjectId(user_id), weekly=WeeklyStats(
            week_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    weekly_stats = statistics["weekly"]
    return Statistics(
        user_id=ObjectId(user_id),
        weekly=WeeklyStats(
            week_start=start_date,
            distance=weekly_stats["distance"],
            duration=weekly_stats["duration"],
            count=weekly_stats["count"],
            average_pace=weekly_stats["average_pace"]
        )
    )

@router.get("/monthly/{user_id}", response_model=Statistics)
async def get_monthly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)

    if not statistics or "monthly" not in statistics:
        return Statistics(user_id=ObjectId(user_id), monthly=MonthlyStats(
            month_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    monthly_stats = statistics["monthly"]
    return Statistics(
        user_id=ObjectId(user_id),
        monthly=MonthlyStats(
            month_start=start_date,
            distance=monthly_stats["distance"],
            duration=monthly_stats["duration"],
            count=monthly_stats["count"],
            average_pace=monthly_stats["average_pace"]
        )
    )

@router.get("/yearly/{user_id}", response_model=Statistics)
async def get_yearly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    
    if not statistics or "yearly" not in statistics:
        return Statistics(user_id=ObjectId(user_id), yearly=YearlyStats(
            year_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    yearly_stats = statistics["yearly"]
    return Statistics(
        user_id=ObjectId(user_id),
        yearly=YearlyStats(
            year_start=start_date,
            distance=yearly_stats["distance"],
            duration=yearly_stats["duration"],
            count=yearly_stats["count"],
            average_pace=yearly_stats["average_pace"]
        )
    )

@router.get("/all_time/{user_id}", response_model=Statistics)
async def get_all_time_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})


    if not statistics or "totally" not in statistics:
        return Statistics(user_id=ObjectId(user_id), totally=TotalStats(
            year_start=datetime.now(timezone.utc),
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    total_stats = statistics["totally"]

    return Statistics(
        user_id=ObjectId(user_id),
        totally=TotalStats(
            year_start=total_stats["year_start"], # 생성일인데 이름만 다름
            distance=total_stats["distance"],
            duration=total_stats["duration"],
            count=total_stats["count"],
            average_pace=total_stats["average_pace"]
        )
    )
    
    
# 그래프 만들기
# 주간 그래프
@router.get("/weekly_data/{user_id}")
async def get_weekly_data(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = today - timedelta(days=today.weekday())
    
    runs = await db.runs.find({"user_id": ObjectId(user_id), "date": {"$gte": start_date}}).to_list(length=None)
    
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    distance_by_day = {day: 0 for day in days}
    
    for run in runs:
        day = days[run['date'].weekday()]
        distance_by_day[day] += run['distance']
    
    x = list(distance_by_day.keys())
    y = list(distance_by_day.values())
    
    return {"x": x, "y": y}

# 월간 그래프
@router.get("/monthly_data/{user_id}")
async def get_monthly_data(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
    
    runs = await db.runs.find({"user_id": ObjectId(user_id), "date": {"$gte": start_date}}).to_list(length=None)
    
    days_in_month = (today.replace(month=today.month % 12 + 1, day=1) - timedelta(days=1)).day
    distance_by_day = {day: 0 for day in range(1, days_in_month + 1)}
    
    for run in runs:
        day = run['date'].day
        distance_by_day[day] += run['distance']
    
    x = list(distance_by_day.keys())
    y = list(distance_by_day.values())
    
    return {"x": x, "y": y}

# 연간 그래프
@router.get("/yearly_data/{user_id}")
async def get_yearly_data(user_id: str, db=Depends(get_database)):
    today = datetime.now(timezone.utc)
    start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
    
    runs = await db.runs.find({"user_id": ObjectId(user_id), "date": {"$gte": start_date}}).to_list(length=None)
    
    distance_by_month = {month: 0 for month in range(1, 13)}
    
    for run in runs:
        month = run['date'].month
        distance_by_month[month] += run['distance']
    
    x = list(distance_by_month.keys())
    y = list(distance_by_month.values())
    
    return {"x": x, "y": y}

# 전체 그래프
@router.get("/all_time_data/{user_id}")
async def get_all_time_data(user_id: str, db=Depends(get_database)):
    runs = await db.runs.find({"user_id": ObjectId(user_id)}).to_list(length=None)
    
    distance_by_year = {}
    
    for run in runs:
        year = run['date'].year
        if year not in distance_by_year:
            distance_by_year[year] = 0
        distance_by_year[year] += run['distance']
    
    x = list(distance_by_year.keys())
    y = list(distance_by_year.values())
    
    return {"x": x, "y": y}






