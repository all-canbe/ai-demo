from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.utils.exceptions import BadRequestException, UnauthorizedException
from app.config.logging_config import get_logger

logger = get_logger(__name__)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, data: RegisterRequest) -> User:
    existing = await get_user_by_email(db, data.email)
    if existing:
        from app.schemas.common import ErrorCode
        raise BadRequestException(
            error_code=ErrorCode.AUTH_USER_EXISTS,
            message="该邮箱已注册",
        )

    user = User(
        email=data.email,
        name=data.name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    logger.info(f"用户注册成功: {user.email}")
    return user


async def authenticate_user(db: AsyncSession, data: LoginRequest) -> tuple[User, str, str]:
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password_hash):
        from app.schemas.common import ErrorCode
        raise UnauthorizedException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            message="邮箱或密码错误",
        )

    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})

    logger.info(f"用户登录成功: {user.email}")
    return user, access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    from app.utils.security import verify_refresh_token, create_access_token

    payload = verify_refresh_token(refresh_token)
    user_id = payload.get("sub")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        from app.schemas.common import ErrorCode
        raise UnauthorizedException(error_code=ErrorCode.AUTH_NOT_LOGGED_IN)

    new_access_token = create_access_token({"sub": user_id})
    logger.info(f"Token刷新成功: {user.email}")
    return new_access_token
