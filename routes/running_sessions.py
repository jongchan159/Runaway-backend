from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from database import get_database
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from models import Run
from typing import List, Optional, Dict

router = APIRouter()

class RunningSessionCreate(BaseModel):
    distance: float
    duration: int
    average_pace: float
    current_pace: float = None
    route: List[Dict[str, float]]
    strength: int = None
    course_id: Optional[str] = None
    
class RunningSessionUpdate(BaseModel):
    current_distance: float
    current_time: float

# 런닝세션 시작
@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_running_session(request: Request, db=Depends(get_database)):
    user_id = request.headers.get("x-user-id")  # 사용자 ID를 요청 헤더에서 가져옴
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID header is missing")
    
    session = {
        "start_time": datetime.now(timezone.utc),
        "status": "in_progress",
        "user_id": ObjectId(user_id)  # 세션에 사용자 ID 저장
    }
    result = await db.running_sessions.insert_one(session)
    return {"session_id": str(result.inserted_id)}


# 러닝세션이 완료되면 DB에 런닝 기록을 저장하고, 특정 사용자의 전체 통계를 업데이트
@router.post("/{session_id}/end")
async def end_running_session(session_id: str, session_data: RunningSessionCreate, db=Depends(get_database)):
    session = await db.running_sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    update_data = {
        "end_time": datetime.now(timezone.utc),
        "distance": session_data.distance,
        "duration": session_data.duration,
        "average_pace": session_data.average_pace,
        "route": session_data.route,
        "status": "completed"
    }

    await db.running_sessions.update_one({"_id": ObjectId(session_id)}, {"$set": update_data})

    # 사용자 통계 업데이트
    user_id = session.get("user_id")
    if user_id:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            try:
                # Run 데이터 생성
                run_data = Run(
                    user_id=user_id,
                    date=datetime.now(timezone.utc),
                    distance=session_data.distance,
                    duration=session_data.duration,
                    average_pace=session_data.average_pace,
                    route=session_data.route,
                    strength=session_data.strength,
                    course_id=ObjectId(session_data.course_id) if session_data.course_id else None
                )
                insert_result = await db.runs.insert_one(run_data.dict(by_alias=True))
                if not insert_result.acknowledged:
                    raise HTTPException(status_code=500, detail="Failed to insert run data")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error occurred while creating run data: {str(e)}")

    return {"message": "Session ended successfully"}



# DB에 저장된 유저의 최근 완료된 세 개의 런닝기록 조회
@router.get("/runs/{user_id}")
async def get_user_running_history(user_id: str, db=Depends(get_database)):
    cursor = db.runs.find({"user_id": ObjectId(user_id)}).sort("date", -1)
    runs = await cursor.to_list(length=3)
    return jsonable_encoder(runs, custom_encoder={ObjectId: str})

# DB에 저장된 특정 사용자의 모든 러닝 기록 조회
@router.get("/all_runs/{user_id}")
async def get_user_runs(user_id: str, db=Depends(get_database)):
    cursor = db.runs.find({"user_id": ObjectId(user_id)}).sort("date", -1)
    runs = await cursor.to_list(length=None)
    return jsonable_encoder(runs, custom_encoder={ObjectId: str})

