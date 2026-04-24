from fastapi import APIRouter
from app.api.deps import DBSession, CurrentUser
from app.schemas.common import ApiResponse
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    UserInfo,
    LoginData,
    RefreshTokenData,
)
from app.services.auth_service import register_user, authenticate_user, refresh_access_token
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(db: DBSession, data: RegisterRequest):
    user = await register_user(db, data)
    return ApiResponse(
        data=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            created_at=user.created_at,
        )
    )


@router.post("/login")
async def login(db: DBSession, data: LoginRequest):
    user, access_token, refresh_token = await authenticate_user(db, data)
    return ApiResponse(
        data=LoginData(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserInfo(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
            ),
        )
    )


@router.post("/refresh")
async def refresh_token(db: DBSession, data: RefreshTokenRequest):
    new_access_token = await refresh_access_token(db, data.refresh_token)
    return ApiResponse(
        data=RefreshTokenData(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    )


@router.post("/logout")
async def logout(current_user: CurrentUser):
    return ApiResponse(message="登出成功")


@router.get("/me")
async def get_me(current_user: CurrentUser):
    return ApiResponse(
        data=UserInfo(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            created_at=current_user.created_at,
        )
    )
