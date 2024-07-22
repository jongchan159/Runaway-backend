# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from datetime import timedelta
# from utils import create_user, create_access_token, create_refresh_token, decode_token, authenticate_user
# from database import get_database
# from settings import settings

# router = APIRouter()


# # 토큰 갱신 엔드포인트
# @router.post("/refresh", response_model=Token)
# async def refresh_access_token(request: RefreshTokenRequest, db=Depends(get_database)):
#     payload = decode_token(request.refresh_token)
#     if payload is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     username: str = payload.get("sub")
#     if username is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     user = await db.users.find_one({"username": username})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"sub": user["username"]}, expires_delta=access_token_expires
#     )
#     return {"access_token": access_token, "refresh_token": request.refresh_token, "token_type": "bearer"}
