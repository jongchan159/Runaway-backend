from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from database import get_database
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from models import Run

router = APIRouter()

class RunningSessionCreate(BaseModel):
    distance: float
    duration: int
    average_pace: float
    current_pace: float
    route: list
    
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
            # 기존 통계 업데이트
            today = datetime.now(timezone.utc)
            week_start = today - timedelta(days=today.weekday())
            week_start = datetime(week_start.year, week_start.month, week_start.day, tzinfo=timezone.utc)
            month_start = datetime(today.year, today.month, 1, tzinfo=timezone.utc)
            year_start = datetime(today.year, 1, 1, tzinfo=timezone.utc)

            running_stats = user.get("running_stats", {})

            # 주간 통계 업데이트
            weekly_stats = next((item for item in running_stats.get("weekly", []) if item["week_start"] == week_start.isoformat()), None)
            if weekly_stats:
                weekly_stats["distance"] += session_data.distance
                weekly_stats["duration"] += session_data.duration
                weekly_stats["count"] += 1
                weekly_stats["average_pace"] = weekly_stats["duration"] / weekly_stats["distance"]
            else:
                running_stats.setdefault("weekly", []).append({
                    "week_start": week_start.isoformat(),
                    "distance": session_data.distance,
                    "duration": session_data.duration,
                    "count": 1,
                    "average_pace": session_data.duration / session_data.distance
                })

            # 월간 통계 업데이트
            monthly_stats = next((item for item in running_stats.get("monthly", []) if item["month_start"] == month_start.isoformat()), None)
            if monthly_stats:
                monthly_stats["distance"] += session_data.distance
                monthly_stats["duration"] += session_data.duration
                monthly_stats["count"] += 1
                monthly_stats["average_pace"] = monthly_stats["duration"] / monthly_stats["distance"]
            else:
                running_stats.setdefault("monthly", []).append({
                    "month_start": month_start.isoformat(),
                    "distance": session_data.distance,
                    "duration": session_data.duration,
                    "count": 1,
                    "average_pace": session_data.duration / session_data.distance
                })

            # 연간 통계 업데이트
            yearly_stats = next((item for item in running_stats.get("yearly", []) if item["year_start"] == year_start.isoformat()), None)
            if yearly_stats:
                yearly_stats["distance"] += session_data.distance
                yearly_stats["duration"] += session_data.duration
                yearly_stats["count"] += 1
                yearly_stats["average_pace"] = yearly_stats["duration"] / yearly_stats["distance"]
            else:
                running_stats.setdefault("yearly", []).append({
                    "year_start": year_start.isoformat(),
                    "distance": session_data.distance,
                    "duration": session_data.duration,
                    "count": 1,
                    "average_pace": session_data.duration / session_data.distance
                })

            # 전체 통계 업데이트
            total_distance = running_stats.get("total_distance", {
                "year_start": year_start.isoformat(),
                "distance": 0,
                "duration": 0,
                "count": 0,
                "average_pace": 0
            })
            total_distance["distance"] += session_data.distance
            total_distance["duration"] += session_data.duration
            total_distance["count"] += 1
            total_distance["average_pace"] = total_distance["duration"] / total_distance["distance"]

            running_stats["total_distance"] = total_distance

            await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"running_stats": running_stats}})

            # Run 데이터 생성
            run_data = Run(
                user_id=user_id,
                date=datetime.now(timezone.utc),
                distance=session_data.distance,
                duration=session_data.duration,
                average_pace=session_data.average_pace,
                route=session_data.route,
                course_type=session.get("course_type"),
                course_id=session.get("course_id")
            )
            await db.runs.insert_one(run_data.dict(by_alias=True))
    
    return {"message": "Session ended successfully"}

# DB에 저장된 유저의 최근 완료된 세 개의 런닝기록 조회
@router.get("/runs/{user_id}")
async def get_user_running_history(user_id: str, db=Depends(get_database)):
    cursor = db.running_sessions.find({"user_id": ObjectId(user_id), "status": "completed"}).sort("start_time", -1).limit(3)
    sessions = await cursor.to_list(length=3)
    return jsonable_encoder(sessions, custom_encoder={ObjectId: str})

# DB에 저장된 특정 사용자의 모든 러닝 기록 조회
@router.get("/all_runs/{user_id}")
async def get_user_runs(user_id: str, db=Depends(get_database)):
    cursor = db.runs.find({"user_id": ObjectId(user_id)}).sort("date", -1)
    runs = await cursor.to_list(length=None)
    return jsonable_encoder(runs, custom_encoder={ObjectId: str})



# # WebSocket 연결을 통해 실시간으로 평균 페이스와 현재 페이스 값을 갱신
# @router.websocket("/ws/{session_id}")
# async def websocket_endpoint(websocket: WebSocket, session_id: str, db=Depends(get_database)):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_json()
#             current_distance = data.get("current_distance")
#             current_time = data.get("current_time")

#             # 현재 페이스 계산
#             current_pace = current_time / current_distance if current_distance > 0 else 0
            
#             # 세션에서 현재까지의 거리와 시간을 업데이트
#             await db.running_sessions.update_one(
#                 {"_id": ObjectId(session_id)},
#                 {"$set": {"distance": current_distance, "duration": current_time, "current_pace": current_pace}}
#             )

#             # 평균 페이스 계산 (10초마다)
#             session = await db.running_sessions.find_one({"_id": ObjectId(session_id)})
#             if session:
#                 total_distance = session.get("distance", 0)
#                 total_duration = session.get("duration", 0)
#                 average_pace = total_duration / total_distance if total_distance > 0 else 0

#                 await websocket.send_json({
#                     "current_pace": current_pace,
#                     "average_pace": average_pace
#                 })

#             await asyncio.sleep(1)
#     except WebSocketDisconnect:
#         print("WebSocket disconnected")