from app.tasks.celery_app import celery_app
from app.config.logging_config import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="app.tasks.embedding_tasks.generate_embeddings",
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    soft_time_limit=300,
)
def generate_embeddings(self, document_id: str, parse_result_dict: dict):
    from app.processing.embedding import generate_embeddings as do_generate
    from app.storage.milvus_client import milvus_client

    try:
        result = do_generate(parse_result_dict, document_id)

        if result.chunks and result.embeddings:
            milvus_client.insert_chunks(result.chunks, result.embeddings)

        logger.info(f"向量生成和存储完成: {document_id}, {len(result.embeddings)} 个向量")
        return result.to_dict()

    except Exception as exc:
        logger.error(f"向量生成失败: {document_id}, 错误: {exc}")
        raise self.retry(exc=exc)
