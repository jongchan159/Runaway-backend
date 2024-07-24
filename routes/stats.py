from fastapi import APIRouter, Depends, HTTPException
from database import get_database
from datetime import datetime, timedelta, timezone
from bson import ObjectId
from models import Statistics, WeeklyStats, MonthlyStats, YearlyStats, TotalStats

router = APIRouter()

@router.get("/weekly/{user_id}", response_model=Statistics)
async def get_weekly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    print(f"Fetched statistics for weekly: {statistics}")  # 디버깅 로그 추가

    if not statistics or "weekly" not in statistics:
        today = datetime.now(timezone.utc)
        start_date = today - timedelta(days=today.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
        return Statistics(user_id=ObjectId(user_id), weekly=WeeklyStats(
            week_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    weekly_stats = statistics["weekly"]
    print(f"Weekly stats: {weekly_stats}")  # 디버깅 로그 추가
    return Statistics(
        user_id=ObjectId(user_id),
        weekly=WeeklyStats(
            week_start=weekly_stats["week_start"],
            distance=weekly_stats["distance"],
            duration=weekly_stats["duration"],
            count=weekly_stats["count"],
            average_pace=weekly_stats["average_pace"]
        )
    )

@router.get("/monthly/{user_id}", response_model=Statistics)
async def get_monthly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    print(f"Fetched statistics for monthly: {statistics}")  # 디버깅 로그 추가

    if not statistics or "monthly" not in statistics:
        today = datetime.now(timezone.utc)
        start_date = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
        return Statistics(user_id=ObjectId(user_id), monthly=MonthlyStats(
            month_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    monthly_stats = statistics["monthly"]
    print(f"Monthly stats: {monthly_stats}")  # 디버깅 로그 추가
    return Statistics(
        user_id=ObjectId(user_id),
        monthly=MonthlyStats(
            month_start=monthly_stats["month_start"],
            distance=monthly_stats["distance"],
            duration=monthly_stats["duration"],
            count=monthly_stats["count"],
            average_pace=monthly_stats["average_pace"]
        )
    )

@router.get("/yearly/{user_id}", response_model=Statistics)
async def get_yearly_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    print(f"Fetched statistics for yearly: {statistics}")  # 디버깅 로그 추가

    if not statistics or "yearly" not in statistics:
        today = datetime.now(timezone.utc)
        start_date = datetime(today.year, 1, 1, tzinfo=timezone.utc)
        return Statistics(user_id=ObjectId(user_id), yearly=YearlyStats(
            year_start=start_date,
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    yearly_stats = statistics["yearly"]
    print(f"Yearly stats: {yearly_stats}")  # 디버깅 로그 추가
    return Statistics(
        user_id=ObjectId(user_id),
        yearly=YearlyStats(
            year_start=yearly_stats["year_start"],
            distance=yearly_stats["distance"],
            duration=yearly_stats["duration"],
            count=yearly_stats["count"],
            average_pace=yearly_stats["average_pace"]
        )
    )

@router.get("/all_time/{user_id}", response_model=Statistics)
async def get_all_time_stats(user_id: str, db=Depends(get_database)):
    statistics = await db.statistics.find_one({"user_id": ObjectId(user_id)})
    print(f"Fetched statistics for all time: {statistics}")  # 디버깅 로그 추가

    if not statistics or "totally" not in statistics:
        return Statistics(user_id=ObjectId(user_id), totally=TotalStats(
            year_start=datetime.now(timezone.utc),
            distance=0,
            duration=0,
            count=0,
            average_pace=0
        ))
    
    total_stats = statistics["totally"]
    print(f"Total stats: {total_stats}")  # 디버깅 로그 추가
    return Statistics(
        user_id=ObjectId(user_id),
        totally=TotalStats(
            year_start=total_stats["year_start"], # 여기 고쳐야함
            distance=total_stats["distance"],
            duration=total_stats["duration"],
            count=total_stats["count"],
            average_pace=total_stats["average_pace"]
        )
    )






