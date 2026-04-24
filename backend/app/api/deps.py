from typing import Annotated
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import get_db
from app.models.user import User
from app.utils.security import verify_access_token
from app.utils.exceptions import UnauthorizedException
from app.schemas.common import ErrorCode

DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DBSession,
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization:
        raise UnauthorizedException(error_code=ErrorCode.AUTH_NOT_LOGGED_IN)

    token = authorization.replace("Bearer ", "")
    payload = verify_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise UnauthorizedException(error_code=ErrorCode.AUTH_INVALID_TOKEN)

    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException(error_code=ErrorCode.AUTH_NOT_LOGGED_IN)

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_user_optional(
    db: DBSession,
    authorization: str | None = Header(default=None),
) -> User | None:
    if not authorization:
        return None

    try:
        return await get_current_user(db, authorization)
    except (UnauthorizedException, HTTPException):
        return None
