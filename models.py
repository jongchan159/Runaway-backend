from bson import ObjectId
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any
from bson.binary import Binary

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
    duration: float
    average_pace: float
    strength: Optional[int] = None
    route: List[Dict[str, Any]]
    course_type: Optional[str] = None
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
    duration: float
    count: int
    average_pace: float

class MonthlyStats(BaseModel):
    month_start: datetime
    distance: float
    duration: float
    count: int
    average_pace: float

class YearlyStats(BaseModel):
    year_start: datetime
    distance: float
    duration: float
    count: int
    average_pace: float

class TotalStats(BaseModel):
    year_start: datetime
    distance: float
    duration: float
    count: int
    average_pace: float

class Statistics(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    weekly: Optional[List[WeeklyStats]] = None
    monthly: Optional[List[MonthlyStats]] = None
    yearly: Optional[List[YearlyStats]] = None
    totally: Optional[TotalStats] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class Session(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    running_time: datetime
    distance: float
    average_pace: float
    current_pace: float
    strength: int = 0
    route: Dict[str, Any]
    status: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


