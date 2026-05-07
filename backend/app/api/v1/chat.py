import math
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.api.deps import DBSession, CurrentUser
from app.schemas.common import ApiResponse, PaginatedData
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionItem, ChatHistoryData
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def send_chat_message_stream(
    db: DBSession,
    current_user: CurrentUser,
    data: ChatRequest,
):
    async def generate():
        async for chunk in chat_service.stream_chat_message(
            user=current_user,
            message=data.message,
            document_ids=data.document_ids,
            chat_id=data.chat_id,
        ):
            yield chunk
    
    return StreamingResponse(generate(), media_type="text/plain")


@router.post("")
async def send_chat_message(
    db: DBSession,
    current_user: CurrentUser,
    data: ChatRequest,
):
    result = await chat_service.send_chat_message(
        db=db,
        user=current_user,
        message=data.message,
        document_ids=data.document_ids,
        chat_id=data.chat_id,
    )
    return ApiResponse(data=ChatResponse(**result))


@router.post("/sessions")
async def create_chat_session(
    db: DBSession,
    current_user: CurrentUser,
    document_ids: list[str],
):
    chat_session = await chat_service.create_chat_session(
        db=db,
        user=current_user,
        document_ids=document_ids,
    )
    return ApiResponse(data=ChatSessionItem(
        id=chat_session.id,
        title=chat_session.title,
        created_at=chat_session.created_at,
    ))


@router.get("/sessions")
async def get_chat_sessions(
    db: DBSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    sessions, total = await chat_service.get_chat_sessions(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
    )
    items = [
        ChatSessionItem(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
        )
        for s in sessions
    ]
    return ApiResponse(
        data=PaginatedData(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=math.ceil(total / page_size) if total > 0 else 0,
        )
    )


@router.get("/{chat_id}")
async def get_chat_history(
    db: DBSession,
    current_user: CurrentUser,
    chat_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    result = await chat_service.get_chat_history(
        db=db,
        user=current_user,
        chat_id=chat_id,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(data=ChatHistoryData(**result))


@router.delete("/{chat_id}")
async def delete_chat_session(
    db: DBSession,
    current_user: CurrentUser,
    chat_id: str,
):
    await chat_service.delete_chat_session(db, chat_id, current_user)
    return ApiResponse(message="聊天会话删除成功")
