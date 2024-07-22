import secrets

def generate_secret_key(length: int = 32) -> str:
    return secrets.token_hex(length)

# 환경 변수 설정
env_vars = {
    "MONGODB_URL": "mongodb+srv://jongchan159:R81Qm2sa6280LZ18@runawaycluster.cocuidj.mongodb.net/?retryWrites=true&w=majority&appName=RunawayCluster",
    "SECRET_KEY": generate_secret_key(),
    "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "REFRESH_TOKEN_EXPIRE_DAYS": "7",
    "ALGORITHM": "HS256"
}

# .env 파일에 저장
with open(".env", "w") as f:
    for key, value in env_vars.items():
        f.write(f"{key}={value}\n")

print(f"Secret Key generated and saved to .env")