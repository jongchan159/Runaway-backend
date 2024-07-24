from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson.binary import Binary


# 데이터베이스에 저장될 형식 정의
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, values=None, **kwargs):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema.update(type='string')
        return json_schema

class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    hashed_password: Optional[str] = None
    created_at: datetime
    running_stats: Optional[Dict[str, Any]] = None
    recent_runs: Optional[List[Dict[str, Any]]] = None
    refresh_token: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class Run(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    date: datetime
    distance: float
    duration: int
    average_pace: float
    strength: Optional[int] = 5
    route: Optional[List[Dict[str, Any]]]
    course_id: Optional[PyObjectId] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class Course(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_by: Optional[PyObjectId] = None
    route: Binary
    route_coordinate: Dict[str, Any]
    distance: float
    course_type: Optional[int] = 0 #0이면 직접그리기, 1이면 추천
    recommendation_count: int = 0
    created_at: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class WeeklyStats(BaseModel):
    week_start: datetime
    distance: float
    duration: int
    count: int
    average_pace: float

class MonthlyStats(BaseModel):
    month_start: datetime
    distance: float
    duration: int
    count: int
    average_pace: float

class YearlyStats(BaseModel):
    year_start: datetime
    distance: float
    duration: int
    count: int
    average_pace: float

class TotalStats(BaseModel):
    year_start: datetime
    distance: float
    duration: int
    count: int
    average_pace: float

class Statistics(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    weekly: Optional[WeeklyStats] = None
    monthly: Optional[MonthlyStats] = None
    yearly: Optional[YearlyStats] = None
    totally: Optional[TotalStats] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

