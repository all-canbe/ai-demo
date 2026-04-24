from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.folder import Folder
from app.models.document import Document
from app.models.user import User
from app.utils.exceptions import NotFoundException, BadRequestException
from app.schemas.common import ErrorCode
from app.config.logging_config import get_logger

logger = get_logger(__name__)


async def create_folder(
    db: AsyncSession,
    user: User,
    name: str,
    parent_id: str | None = None,
) -> Folder:
    if parent_id:
        parent = await _get_folder(db, parent_id, user.id)
        if not parent:
            raise NotFoundException(
                error_code=ErrorCode.DOC_NOT_FOUND,
                message="父文件夹不存在",
            )

    folder = Folder(
        user_id=user.id,
        parent_id=parent_id,
        name=name,
    )
    db.add(folder)
    await db.flush()
    await db.refresh(folder)

    logger.info(f"文件夹创建成功: {folder.id}, 名称: {name}")
    return folder


async def get_folder_list(
    db: AsyncSession,
    user: User,
    parent_id: str | None = None,
) -> list[Folder]:
    query = select(Folder).where(Folder.user_id == user.id)

    if parent_id:
        query = query.where(Folder.parent_id == parent_id)
    else:
        query = query.where(Folder.parent_id.is_(None))

    query = query.order_by(Folder.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_folder_detail(db: AsyncSession, folder_id: str, user: User) -> Folder:
    folder = await _get_folder(db, folder_id, user.id)
    if not folder:
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件夹不存在",
        )
    return folder


async def update_folder(
    db: AsyncSession,
    folder_id: str,
    user: User,
    name: str | None = None,
    parent_id: str | None = None,
) -> Folder:
    folder = await _get_folder(db, folder_id, user.id)
    if not folder:
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件夹不存在",
        )

    if name is not None:
        folder.name = name

    if parent_id is not None:
        if parent_id == folder_id:
            raise BadRequestException(
                error_code=ErrorCode.PARAM_FORMAT_ERROR,
                message="不能将文件夹移动到自身",
            )
        if parent_id:
            parent = await _get_folder(db, parent_id, user.id)
            if not parent:
                raise NotFoundException(
                    error_code=ErrorCode.DOC_NOT_FOUND,
                    message="目标文件夹不存在",
                )
        folder.parent_id = parent_id

    await db.flush()
    await db.refresh(folder)

    logger.info(f"文件夹更新成功: {folder_id}")
    return folder


async def delete_folder(db: AsyncSession, folder_id: str, user: User) -> bool:
    folder = await _get_folder(db, folder_id, user.id)
    if not folder:
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文件夹不存在",
        )

    child_count = await db.scalar(
        select(func.count()).where(Folder.parent_id == folder_id)
    )
    if child_count and child_count > 0:
        raise BadRequestException(
            error_code=ErrorCode.PARAM_FORMAT_ERROR,
            message="文件夹下还有子文件夹，请先删除子文件夹",
        )

    doc_count = await db.scalar(
        select(func.count()).where(Document.folder_id == folder_id)
    )
    if doc_count and doc_count > 0:
        raise BadRequestException(
            error_code=ErrorCode.PARAM_FORMAT_ERROR,
            message="文件夹下还有文档，请先删除或移动文档",
        )

    await db.delete(folder)
    await db.flush()

    logger.info(f"文件夹删除成功: {folder_id}")
    return True


async def _get_folder(db: AsyncSession, folder_id: str, user_id: str) -> Folder | None:
    result = await db.execute(
        select(Folder).where(Folder.id == folder_id, Folder.user_id == user_id)
    )
    return result.scalar_one_or_none()
