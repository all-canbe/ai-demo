import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config.settings import settings
from app.config.logging_config import setup_logging
from app.api.v1.router import router as v1_router, ws_router
from app.schemas.common import ApiResponse, ErrorCode
from app.utils.exceptions import AppException

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    logger.info(f"启动 {settings.PROJECT_NAME} v{settings.VERSION}")

    try:
        from app.models.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.info("PostgreSQL连接正常")
    except Exception as e:
        logger.warning(f"PostgreSQL连接失败: {e}")

    try:
        from app.integrations.cache import cache_service
        if cache_service.ping():
            logger.info("Redis连接正常")
        else:
            logger.warning("Redis连接失败")
    except Exception as e:
        logger.warning(f"Redis连接失败: {e}")

    try:
        from app.storage.neo4j_client import neo4j_client
        neo4j_client.verify_connectivity()
        logger.info("Neo4j连接正常")
    except Exception as e:
        logger.warning(f"Neo4j连接失败: {e}")

    try:
        from app.storage.milvus_client import milvus_client
        milvus_client.list_collections()
        logger.info("Milvus连接正常")
    except Exception as e:
        logger.warning(f"Milvus连接失败: {e}")

    yield

    logger.info("关闭服务，释放资源...")

    from app.storage.milvus_client import milvus_client
    from app.storage.neo4j_client import neo4j_client
    from app.integrations.cache import cache_service

    milvus_client.close()
    neo4j_client.close()
    cache_service.close()

    from app.models.database import engine
    await engine.dispose()

    logger.info("资源释放完成")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)
app.include_router(ws_router, prefix="/ws")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            code=exc.error_code,
            message=exc.message,
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    field = ".".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "参数校验失败")
    message = f"{field}: {msg}" if field else msg
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            code=ErrorCode.PARAM_FORMAT_ERROR,
            message=message,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            code=ErrorCode.SYS_INTERNAL_ERROR,
            message="内部服务错误",
        ).model_dump(),
    )
