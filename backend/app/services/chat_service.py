import math
import json
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import ChatSession, ChatMessage, MessageRole
from app.models.document import Document, ProcessingStatus
from app.models.user import User
from app.storage.milvus_client import milvus_client
from app.storage.neo4j_client import neo4j_client
from app.integrations.llm import llm_service
from app.integrations.cache import cache_service
from app.processing.embedding import embed_query
from app.utils.exceptions import NotFoundException, BadRequestException, InternalServerErrorException
from app.schemas.common import ErrorCode
from app.config.logging_config import get_logger

logger = get_logger(__name__)

CHAT_SYSTEM_PROMPT = """你是一个智能文档助手。根据以下检索到的文档内容回答用户的问题。
请基于提供的文档内容进行回答，如果文档中没有相关信息，请如实说明。
回答时请引用相关文档的内容。

检索到的文档内容：
{context}
"""


async def create_chat_session(
    db: AsyncSession,
    user: User,
    document_ids: list[str],
) -> ChatSession:
    chat_session = ChatSession(
        user_id=user.id,
        title="新会话",
    )
    db.add(chat_session)
    await db.flush()
    await db.refresh(chat_session)
    logger.info(f"创建聊天会话: {chat_session.id}")
    return chat_session


async def send_chat_message(
    db: AsyncSession,
    user: User,
    message: str,
    document_ids: list[str],
    chat_id: str | None = None,
) -> dict:
    if not message.strip():
        raise BadRequestException(
            error_code=ErrorCode.CHAT_MESSAGE_EMPTY,
            message="问题不能为空",
        )

    for doc_id in document_ids:
        result = await db.execute(
            select(Document).where(
                Document.id == doc_id,
                Document.user_id == user.id,
                Document.processing_status == ProcessingStatus.COMPLETED,
            )
        )
        if not result.scalar_one_or_none():
            raise NotFoundException(
                error_code=ErrorCode.DOC_NOT_FOUND,
                message=f"文档不存在或未处理完成: {doc_id}",
            )

    if chat_id:
        session_result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == chat_id,
                ChatSession.user_id == user.id,
            )
        )
        chat_session = session_result.scalar_one_or_none()
        if not chat_session:
            raise NotFoundException(
                error_code=ErrorCode.CHAT_SESSION_NOT_FOUND,
                message="聊天会话不存在",
            )
    else:
        chat_session = ChatSession(
            user_id=user.id,
            title=message[:50],
        )
        db.add(chat_session)
        await db.flush()
        await db.refresh(chat_session)
        chat_id = chat_session.id

    user_msg = ChatMessage(
        session_id=chat_id,
        role=MessageRole.USER,
        content=message,
    )
    db.add(user_msg)
    await db.flush()

    context = await _retrieve_context(document_ids, message)

    system_prompt = CHAT_SYSTEM_PROMPT.format(context=context)
    try:
        ai_response = await llm_service.agenerate(message, system_prompt=system_prompt)
    except Exception as e:
        logger.error(f"LLM调用失败: {e}")
        raise InternalServerErrorException(
            error_code=ErrorCode.CHAT_LLM_FAILED,
            message="LLM调用失败，请稍后重试",
        )

    references = _extract_references(context, document_ids)

    assistant_msg = ChatMessage(
        session_id=chat_id,
        role=MessageRole.ASSISTANT,
        content=ai_response,
        references=json.dumps([r.model_dump() for r in references]) if references else None,
    )
    db.add(assistant_msg)
    await db.flush()

    from app.schemas.chat import ChatResponse, Reference
    return {
        "id": assistant_msg.id,
        "chat_id": chat_id,
        "message": ai_response,
        "references": references,
        "timestamp": assistant_msg.created_at,
    }


async def stream_chat_message(
    user: User,
    message: str,
    document_ids: list[str],
    chat_id: str | None = None,
):
    context = await _retrieve_context(document_ids, message)
    system_prompt = CHAT_SYSTEM_PROMPT.format(context=context)

    async for chunk in llm_service.agenerate_stream(message, system_prompt=system_prompt):
        yield chunk


async def get_chat_history(
    db: AsyncSession,
    user: User,
    chat_id: str,
    page: int = 1,
    page_size: int = 50,
) -> dict:
    session_result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == chat_id,
            ChatSession.user_id == user.id,
        )
    )
    chat_session = session_result.scalar_one_or_none()
    if not chat_session:
        raise NotFoundException(
            error_code=ErrorCode.CHAT_SESSION_NOT_FOUND,
            message="聊天会话不存在",
        )

    count_query = select(func.count()).where(ChatMessage.session_id == chat_id)
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == chat_id)
        .order_by(ChatMessage.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    messages = list(result.scalars().all())

    from app.schemas.chat import ChatMessageItem, Reference

    items = []
    for msg in messages:
        refs = None
        if msg.references:
            try:
                refs_data = json.loads(msg.references)
                refs = [Reference(**r) for r in refs_data]
            except (json.JSONDecodeError, TypeError):
                refs = None

        items.append(ChatMessageItem(
            id=msg.id,
            role=msg.role.value,
            message=msg.content,
            references=refs,
            timestamp=msg.created_at,
        ))

    return {
        "id": chat_id,
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0,
    }


async def get_chat_sessions(
    db: AsyncSession,
    user: User,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[ChatSession], int]:
    query = select(ChatSession).where(ChatSession.user_id == user.id)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(ChatSession.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    sessions = list(result.scalars().all())

    return sessions, total


async def delete_chat_session(db: AsyncSession, chat_id: str, user: User) -> bool:
    session_result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == chat_id,
            ChatSession.user_id == user.id,
        )
    )
    chat_session = session_result.scalar_one_or_none()
    if not chat_session:
        raise NotFoundException(
            error_code=ErrorCode.CHAT_SESSION_NOT_FOUND,
            message="聊天会话不存在",
        )

    await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == chat_id)
    )

    from sqlalchemy import delete
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == chat_id))
    await db.delete(chat_session)
    await db.flush()

    logger.info(f"聊天会话删除: {chat_id}")
    return True


async def _retrieve_context(document_ids: list[str], query: str) -> str:
    context_parts = []

    try:
        query_embedding = embed_query(query)
        vector_results = milvus_client.search(
            query_embedding=query_embedding,
            document_ids=document_ids,
            top_k=5,
        )
        for vr in vector_results:
            context_parts.append(f"[文档:{vr['document_id']}, 页码:{vr['page']}]\n{vr['content']}")
    except Exception as e:
        logger.warning(f"向量检索失败: {e}")

    try:
        keywords = query.split()[:5]
        entity_results = neo4j_client.search_entities(document_ids, keywords)
        for er in entity_results:
            context_parts.append(f"[实体:{er.get('name', '')}, 类型:{er.get('type', [])}]\n{er.get('description', '')}")
    except Exception as e:
        logger.warning(f"图谱检索失败: {e}")

    return "\n\n".join(context_parts) if context_parts else "未检索到相关文档内容"


def _extract_references(context: str, document_ids: list[str]) -> list:
    from app.schemas.chat import Reference

    references = []
    seen = set()

    for line in context.split("\n"):
        if line.startswith("[文档:") and ", 页码:" in line:
            try:
                doc_part = line.split("[文档:")[1].split(", 页码:")[0]
                page_part = line.split(", 页码:")[1].split("]")[0]
                doc_id = doc_part.strip()
                page = int(page_part.strip())

                ref_key = f"{doc_id}:{page}"
                if ref_key not in seen:
                    seen.add(ref_key)
                    content_start = line.find("]\n")
                    content = line[content_start + 2:] if content_start >= 0 else ""
                    references.append(Reference(
                        document_id=doc_id,
                        page=page,
                        content=content[:200],
                    ))
            except (ValueError, IndexError):
                continue

    return references
