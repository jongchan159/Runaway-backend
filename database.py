from motor.motor_asyncio import AsyncIOMotorClient
from settings import settings

# 클라이언트를 글로벌로 유지하여 재사용
client = None

async def connect_to_mongo():
    global client
    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL, tls=True, tlsAllowInvalidCertificates=True)
        await client.server_info()  # 연결 확인
        print("Successfully connected to MongoDB")
        # 인덱스 생성
        db = client.get_database("RunawayCluster")
        await db.courses.create_index([("route_coordinate", "2dsphere")])

async def close_mongo_connection():
    global client
    if client:
        client.close()
        client = None
        print("MongoDB connection closed")

def get_database():
    global client
    return client.get_database("RunawayCluster") if client else None
