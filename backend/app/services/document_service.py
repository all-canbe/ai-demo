import math
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, ProcessingStatus
from app.models.user import User
from app.storage.file_storage import get_upload_path, save_upload_file, delete_file
from app.storage.milvus_client import milvus_client
from app.storage.neo4j_client import neo4j_client
from app.utils.exceptions import BadRequestException, NotFoundException, InternalServerErrorException
from app.schemas.common import ErrorCode
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)


async def upload_document(
    db: AsyncSession,
    user: User,
    file_content: bytes,
    filename: str,
    folder_id: str | None = None,
) -> Document:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_FILE_TYPES:
        raise BadRequestException(
            error_code=ErrorCode.PARAM_FILE_TYPE_NOT_SUPPORTED,
            message=f"不支持的文件类型: {ext}",
        )

    if len(file_content) > settings.MAX_UPLOAD_SIZE:
        raise BadRequestException(
            error_code=ErrorCode.PARAM_FILE_TOO_LARGE,
            message="文件大小超过限制",
        )

    file_path = get_upload_path(user.id, filename)
    await save_upload_file(file_content, file_path)

    document = Document(
        user_id=user.id,
        folder_id=folder_id,
        name=filename,
        type=ext,
        size=len(file_content),
        file_path=file_path,
        processing_status=ProcessingStatus.PENDING,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    from app.tasks.document_tasks import process_document
    process_document.delay(document.id)

    logger.info(f"文档上传成功: {document.id}, 名称: {filename}")
    return document


async def get_document_list(
    db: AsyncSession,
    user: User,
    folder_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Document], int]:
    query = select(Document).where(Document.user_id == user.id)

    if folder_id is not None:
        query = query.where(Document.folder_id == folder_id)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    sort_column = getattr(Document, sort_by, Document.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    documents = list(result.scalars().all())

    return documents, total


async def get_document_detail(db: AsyncSession, document_id: str, user: User) -> Document:
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == user.id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文档不存在",
        )

    return document


async def delete_document(db: AsyncSession, document_id: str, user: User) -> bool:
    document = await get_document_detail(db, document_id, user)

    delete_file(document.file_path)

    try:
        milvus_client.delete_by_document(document_id)
    except Exception as e:
        logger.warning(f"删除向量数据失败: {e}")

    try:
        neo4j_client.delete_document_graph(document_id)
    except Exception as e:
        logger.warning(f"删除知识图谱失败: {e}")

    await db.delete(document)
    await db.flush()

    logger.info(f"文档删除成功: {document_id}")
    return True


async def get_document_status(db: AsyncSession, document_id: str, user: User) -> dict:
    document = await get_document_detail(db, document_id, user)

    progress_map = {
        ProcessingStatus.PENDING: 0,
        ProcessingStatus.PARSING: 25,
        ProcessingStatus.EXTRACTING: 50,
        ProcessingStatus.EMBEDDING: 75,
        ProcessingStatus.COMPLETED: 100,
        ProcessingStatus.FAILED: 0,
        ProcessingStatus.CANCELLED: 0,
    }

    return {
        "id": document.id,
        "processing_status": document.processing_status.value,
        "progress": progress_map.get(document.processing_status, 0),
        "error_message": document.error_message,
        "updated_at": document.updated_at,
    }


async def retry_document(db: AsyncSession, document_id: str, user: User) -> Document:
    document = await get_document_detail(db, document_id, user)

    if document.processing_status not in (ProcessingStatus.FAILED,):
        raise BadRequestException(
            error_code=ErrorCode.DOC_PROCESSING,
            message="仅失败文档可重试",
        )

    document.processing_status = ProcessingStatus.PENDING
    document.error_message = None
    await db.flush()

    from app.tasks.document_tasks import process_document
    process_document.delay(document.id)

    logger.info(f"文档重试处理: {document_id}")
    return document
