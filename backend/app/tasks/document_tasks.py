import asyncio
from app.tasks.celery_app import celery_app
from app.config.logging_config import get_logger

logger = get_logger(__name__)


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(
    name="app.tasks.document_tasks.process_document",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=600,
)
def process_document(self, document_id: str):
    logger.info(f"开始处理文档: {document_id}")

    try:
        _update_status(document_id, "parsing")
        parse_result = parse_document(document_id)

        _update_status(document_id, "extracting")
        extract_result = extract_info(document_id, parse_result)

        _update_status(document_id, "embedding")
        from app.tasks.embedding_tasks import generate_embeddings
        generate_embeddings.delay(document_id, parse_result.to_dict())

        _update_status(document_id, "completed")
        logger.info(f"文档处理完成: {document_id}")

    except Exception as exc:
        logger.error(f"文档处理失败: {document_id}, 错误: {exc}")
        _update_status(document_id, "failed", str(exc))
        raise self.retry(exc=exc)


@celery_app.task(
    name="app.tasks.document_tasks.parse_document",
    bind=True,
    max_retries=2,
    soft_time_limit=300,
)
def parse_document(self, document_id: str):
    from app.processing.parser import parse_document as do_parse

    async def _get_file_path():
        from sqlalchemy import select
        from app.models.database import async_session_factory
        from app.models.document import Document

        async with async_session_factory() as session:
            result = await session.execute(select(Document).where(Document.id == document_id))
            doc = result.scalar_one_or_none()
            return doc.file_path if doc else None

    file_path = _run_async(_get_file_path())
    if not file_path:
        raise ValueError(f"文档不存在: {document_id}")

    result = do_parse(file_path)
    logger.info(f"文档解析完成: {document_id}")
    return result.to_dict()


@celery_app.task(
    name="app.tasks.document_tasks.extract_info",
    bind=True,
    max_retries=2,
    soft_time_limit=120,
)
def extract_info(document_id: str, parse_result_dict: dict):
    from app.processing.extractor import extract_info as do_extract

    result = do_extract(parse_result_dict, document_id)

    from app.storage.neo4j_client import neo4j_client
    neo4j_client.create_document_node(
        document_id,
        parse_result_dict.get("name", ""),
        parse_result_dict.get("type", ""),
    )
    neo4j_client.store_extraction_results(parse_result_dict, result.to_dict(), document_id)

    logger.info(f"信息提取完成: {document_id}")
    return result.to_dict()


def _update_status(document_id: str, status: str, error_message: str | None = None):
    async def _do():
        from sqlalchemy import select, update
        from app.models.database import async_session_factory
        from app.models.document import Document, ProcessingStatus

        async with async_session_factory() as session:
            values = {"processing_status": ProcessingStatus(status)}
            if error_message:
                values["error_message"] = error_message
            await session.execute(
                update(Document).where(Document.id == document_id).values(**values)
            )
            await session.commit()

    _run_async(_do())
    logger.info(f"文档状态更新: {document_id} -> {status}")
