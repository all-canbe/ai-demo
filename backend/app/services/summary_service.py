from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, ProcessingStatus
from app.utils.exceptions import BadRequestException, NotFoundException
from app.schemas.common import ErrorCode
from app.integrations.llm import llm_service
from app.integrations.cache import cache_service
from app.config.logging_config import get_logger

logger = get_logger(__name__)

SUMMARY_PROMPT = """请对以下文档内容生成摘要，包括：
1. 文档主要内容概述
2. 关键要点（3-5个）

请以JSON格式返回：
{
    "summary": "摘要内容",
    "key_points": ["要点1", "要点2", "要点3"]
}

文档内容：
{content}
"""


async def get_document_summary(db: AsyncSession, document_id: str, user_id: str) -> dict:
    from sqlalchemy import select

    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.user_id == user_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise NotFoundException(
            error_code=ErrorCode.DOC_NOT_FOUND,
            message="文档不存在",
        )

    if document.processing_status != ProcessingStatus.COMPLETED:
        raise BadRequestException(
            error_code=ErrorCode.DOC_PROCESSING,
            message="文档尚未处理完成，无法生成摘要",
        )

    import hashlib
    content_hash = hashlib.md5(document_id.encode()).hexdigest()
    cached = cache_service.get_llm_cache(content_hash)
    if cached:
        import json
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            pass

    from app.storage.neo4j_client import neo4j_client
    graph_data = neo4j_client.get_document_graph(document_id)

    content_parts = []
    for node in graph_data.get("nodes", []):
        if node.get("target_name"):
            content_parts.append(f"{node.get('target_type', [])}: {node['target_name']}")

    content = "\n".join(content_parts) if content_parts else f"文档: {document.name}"

    prompt = SUMMARY_PROMPT.format(content=content)
    response = llm_service.generate(prompt)

    import json
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            summary_data = json.loads(response[start:end])
        else:
            summary_data = {
                "summary": response,
                "key_points": [],
            }
    except json.JSONDecodeError:
        summary_data = {
            "summary": response,
            "key_points": [],
        }

    summary_data["document_id"] = document_id

    cache_service.set_llm_cache(content_hash, json.dumps(summary_data, ensure_ascii=False))

    logger.info(f"文档摘要生成完成: {document_id}")
    return summary_data
