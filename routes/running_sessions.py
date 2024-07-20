from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database import get_database
from datetime import datetime, timezone
from bson import ObjectId
from fastapi.encoders import jsonable_encoder

router = APIRouter()

class RunningSessionCreate(BaseModel):
    distance: float
    duration: int
    average_pace: float
    route: list

@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_running_session(db=Depends(get_database)):
    session = {
        "start_time": datetime.now(timezone.utc),
        "status": "in_progress"
    }
    result = await db.running_sessions.insert_one(session)
    return {"session_id": str(result.inserted_id)}

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
    return {"message": "Session ended successfully"}

@router.get("/history")
async def get_running_history(db=Depends(get_database)):
    cursor = db.running_sessions.find({"status": "completed"}).sort("start_time", -1).limit(10)
    sessions = await cursor.to_list(length=10)
    return jsonable_encoder(sessions, custom_encoder={ObjectId: str})