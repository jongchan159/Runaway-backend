from fastapi import FastAPI
from routes import users, running_sessions, courses, stats
from database import connect_to_mongo, close_mongo_connection
from settings import settings

app = FastAPI(title="Runaway API")

# 데이터베이스 연결 이벤트 핸들러
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# 라우터 등록
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(running_sessions.router, prefix="/running_sessions", tags=["running"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])

@app.get("/")
async def root():
    return {"message": "Welcome to Runaway API"}

# 시크릿키 테스트용
@app.get("/test-secret-key")
def test_secret_key():
    return {"secret_key": settings.SECRET_KEY}