import uuid
from typing import Any
from app.config.settings import settings
from app.config.logging_config import get_logger

logger = get_logger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

_openai_client = None


def _get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL
        )
    return _openai_client


class EmbeddingResult:
    def __init__(self):
        self.chunks: list[dict[str, Any]] = []
        self.embeddings: list[list[float]] = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunks": self.chunks,
            "embeddings_count": len(self.embeddings),
        }


def generate_embeddings(
    parse_result_dict: dict[str, Any],
    document_id: str,
) -> EmbeddingResult:
    result = EmbeddingResult()

    chunks = _split_into_chunks(parse_result_dict, document_id)
    if not chunks:
        logger.warning(f"文档 {document_id} 无可分块内容")
        return result

    result.chunks = chunks

    try:
        embeddings = _embed_texts([c["content"] for c in chunks])
        result.embeddings = embeddings
        logger.info(f"向量生成完成: 文档 {document_id}, {len(embeddings)} 个向量")
    except Exception as e:
        logger.error(f"向量生成失败: {e}")
        raise

    return result


def _split_into_chunks(
    parse_result_dict: dict[str, Any],
    document_id: str,
) -> list[dict[str, Any]]:
    chunks = []
    sections = parse_result_dict.get("sections", [])

    for section in sections:
        content = section.get("content", "")
        if not content:
            continue

        page = section.get("page", 0)
        section_id = section.get("id", "")

        if len(content) <= CHUNK_SIZE:
            chunks.append({
                "id": str(uuid.uuid4()),
                "content": content,
                "document_id": document_id,
                "section_id": section_id,
                "page": page,
                "type": "text",
            })
        else:
            start = 0
            while start < len(content):
                end = start + CHUNK_SIZE
                chunk_text = content[start:end]

                chunks.append({
                    "id": str(uuid.uuid4()),
                    "content": chunk_text,
                    "document_id": document_id,
                    "section_id": section_id,
                    "page": page,
                    "type": "text",
                    "start_pos": start,
                    "end_pos": min(end, len(content)),
                })

                start += CHUNK_SIZE - CHUNK_OVERLAP

    for table in parse_result_dict.get("tables", []):
        content = table.get("content", "")
        if content:
            chunks.append({
                "id": str(uuid.uuid4()),
                "content": content,
                "document_id": document_id,
                "section_id": table.get("id", ""),
                "page": table.get("page", 0),
                "type": "table",
            })

    logger.info(f"文档 {document_id} 分块完成: {len(chunks)} 个片段")
    return chunks


def _embed_texts(texts: list[str]) -> list[list[float]]:
    client = _get_openai_client()

    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            response = client.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=batch,
                dimensions=settings.OPENAI_EMBEDDING_DIMENSION,
            )
            all_embeddings.extend([item.embedding for item in response.data])
        except Exception as e:
            logger.error(f"Embedding API调用失败 (batch {i}): {e}")
            raise

    return all_embeddings


def embed_query(query: str) -> list[float]:
    client = _get_openai_client()
    try:
        response = client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=[query],
            dimensions=settings.OPENAI_EMBEDDING_DIMENSION,
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"查询向量生成失败: {e}")
        raise
