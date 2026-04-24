from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    name: str = Field(..., min_length=1, max_length=100, description="用户名")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=1, description="密码")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="刷新令牌")


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserInfo


class RefreshTokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
