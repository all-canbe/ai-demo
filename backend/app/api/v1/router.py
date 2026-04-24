from fastapi import APIRouter
from app.api.v1 import auth, health, documents, chat, folders, ws

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(auth.router)
router.include_router(documents.router)
router.include_router(chat.router)
router.include_router(folders.router)

ws_router = APIRouter()
ws_router.include_router(ws.router)
