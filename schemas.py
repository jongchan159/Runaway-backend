from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        arbitrary_types_allowed = True

class RunCreate(BaseModel):
    date: datetime
    distance: float
    duration: int
    average_pace: float
    strength: Optional[int] = 0
    route: Dict[str, Any]
    course_type: Optional[str] = ""
    course_id: Optional[PyObjectId] = ""

class RunResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    date: datetime
    distance: float
    duration: int
    average_pace: float
    strength: Optional[int] = None
    route: Dict[str, Any]
    course_type: Optional[str] = None
    course_id: Optional[PyObjectId] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        arbitrary_types_allowed = True

class CourseCreate(BaseModel):
    route: Dict[str, Any]
    route_coordinate: Dict[str, Any]
    distance: float
    created_at: datetime

class CourseResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_by: Optional[PyObjectId] = None
    route: Dict[str, Any]
    route_coordinate: Dict[str, Any]
    distance: float
    recommendation_count: int
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        arbitrary_types_allowed = True

class StatisticsResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    weekly: Optional[List[Dict[str, Any]]] = None
    monthly: Optional[List[Dict[str, Any]]] = None
    yearly: Optional[List[Dict[str, Any]]] = None
    totally: Optional[Dict[str, Any]] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        arbitrary_types_allowed = True

class SessionCreate(BaseModel):
    running_time: datetime
    distance: float
    average_pace: float
    current_pace: float
    strength: int
    route: Dict[str, Any]
    status: str

class SessionResponse(BaseModel):
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
        allow_population_by_field_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
        }
        arbitrary_types_allowed = True
