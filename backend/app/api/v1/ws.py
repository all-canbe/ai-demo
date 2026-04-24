import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.utils.security import verify_access_token
from app.utils.exceptions import UnauthorizedException
from app.schemas.common import ErrorCode
from app.services.chat_service import stream_chat_message
from app.config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket连接: {user_id}")

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        logger.info(f"WebSocket断开: {user_id}")

    async def send_json(self, user_id: str, data: dict):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(data)


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="无效的Token")
            return
    except UnauthorizedException:
        await websocket.close(code=4001, reason="认证失败")
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"code": 2002, "message": "消息格式错误"},
                })
                continue

            msg_type = message.get("type", "")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            if msg_type == "chat_message":
                data = message.get("data", {})
                chat_message = data.get("message", "")
                document_ids = data.get("document_ids", [])
                chat_id = data.get("chat_id")

                if not chat_message:
                    await websocket.send_json({
                        "type": "error",
                        "data": {"code": 4002, "message": "问题不能为空"},
                    })
                    continue

                import uuid
                message_id = str(uuid.uuid4())

                await websocket.send_json({
                    "type": "chat_start",
                    "data": {
                        "chat_id": chat_id or str(uuid.uuid4()),
                        "message_id": message_id,
                    },
                })

                full_response = ""
                try:
                    from app.models.user import User
                    from app.models.chat import ChatSession, ChatMessage, MessageRole
                    from app.models.database import async_session_factory
                    from sqlalchemy import select

                    async with async_session_factory() as db:
                        result = await db.execute(select(User).where(User.id == user_id))
                        user = result.scalar_one_or_none()

                    if not user:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"code": 1001, "message": "用户不存在"},
                        })
                        continue

                    if not chat_id:
                        async with async_session_factory() as db:
                            chat_session = ChatSession(
                                user_id=user_id,
                                title=chat_message[:50],
                            )
                            db.add(chat_session)
                            await db.flush()
                            await db.refresh(chat_session)
                            chat_id = chat_session.id
                    else:
                        async with async_session_factory() as db:
                            session_result = await db.execute(
                                select(ChatSession).where(
                                    ChatSession.id == chat_id,
                                    ChatSession.user_id == user_id,
                                )
                            )
                            existing_session = session_result.scalar_one_or_none()
                            if not existing_session:
                                await websocket.send_json({
                                    "type": "error",
                                    "data": {"code": 4001, "message": "聊天会话不存在"},
                                })
                                continue

                    async with async_session_factory() as db:
                        user_msg = ChatMessage(
                            session_id=chat_id,
                            role=MessageRole.USER,
                            content=chat_message,
                        )
                        db.add(user_msg)
                        await db.flush()

                    async for chunk in stream_chat_message(
                        user=user,
                        message=chat_message,
                        document_ids=document_ids,
                        chat_id=chat_id,
                    ):
                        full_response += chunk
                        await websocket.send_json({
                            "type": "chat_chunk",
                            "data": {
                                "message_id": message_id,
                                "content": chunk,
                            },
                        })

                    async with async_session_factory() as db:
                        assistant_msg = ChatMessage(
                            session_id=chat_id,
                            role=MessageRole.ASSISTANT,
                            content=full_response,
                        )
                        db.add(assistant_msg)
                        await db.flush()

                    await websocket.send_json({
                        "type": "chat_end",
                        "data": {
                            "message_id": message_id,
                            "message": full_response,
                            "chat_id": chat_id,
                            "references": [],
                        },
                    })

                except Exception as e:
                    logger.error(f"WebSocket聊天处理失败: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {"code": 4003, "message": "LLM调用失败，请稍后重试"},
                    })
            else:
                await websocket.send_json({
                    "type": "error",
                    "data": {"code": 2001, "message": f"未知消息类型: {msg_type}"},
                })

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(user_id)
