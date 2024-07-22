from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import List, Optional, Dict, Any

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
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
    hashed_password: str = None
    created_at: datetime
    running_stats: Optional[Dict[str, Any]] = None
    recent_runs: Optional[List[Dict[str, Any]]] = None
    refresh_token: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('id', 'created_at')
    def serialize_fields(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

# 달리기 기록
class Run(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    date: datetime
    distance: float
    duration: float
    average_pace: float
    strength: Optional[int] = None
    route: Dict[str, Any]
    course_type: Optional[str] = None
    course_id: Optional[PyObjectId] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('id', 'user_id', 'date', 'course_id')
    def serialize_fields(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

class Course(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_by: Optional[PyObjectId] = None
    route: Dict[str, Any]
    recommendation_count: int = 0
    created_at: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('id', 'created_by', 'created_at')
    def serialize_fields(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

class Statistics(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    weekly: Optional[List[Dict[str, Any]]] = None
    monthly: Optional[List[Dict[str, Any]]] = None
    yearly: Optional[List[Dict[str, Any]]] = None
    total_distance: Optional[Dict[str, Any]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('id', 'user_id')
    def serialize_fields(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        return value

# 저장 JSON 예시
# {
#     "_id": "unique_stat_id",
#     "user_id": "unique_user_id",
#     "weekly": [
#         {
#             "week_start": "2023-07-01T00:00:00Z",
#             "distance": 42.195,
#             "duration": 360,
#             "average_pace": 5.0,
#             "count": 3
#         }
#     ],
#     "monthly": [
#         {
#             "month_start": "2023-07-01T00:00:00Z",
#             "distance": 168.78,
#             "duration": 1440,
#             "average_pace": 5.0,
#             "count": 12
#         }
#     ],
#     "yearly": [
#         {
#             "year_start": "2023-01-01T00:00:00Z",
#             "distance": 2016.96,
#             "duration": 17280,
#             "average_pace": 5.0,
#             "count": 144
#         }
#     ],
#     "total_distance": {
#         "year_start": "2023-01-01T00:00:00Z",
#         "distance": 2016.96,
#         "duration": 17280,
#         "average_pace": 5.0,
#         "count": 144
#     }
# }


# 런닝세션 정보
class Session(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    running_time: datetime
    distance: float
    average_pace: float
    current_pace: float
    strength: int
    route: Dict[str, Any]
    status: str

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    @field_serializer('id', 'user_id', 'running_time')
    def serialize_fields(cls, value):
        if isinstance(value, ObjectId):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

