from fastapi import APIRouter
from app.schemas.common import ApiResponse
from app.config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    services = {}

    try:
        from app.models.database import engine
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        services["postgresql"] = "connected"
    except Exception as e:
        services["postgresql"] = f"disconnected: {str(e)[:50]}"

    try:
        from app.storage.neo4j_client import neo4j_client
        if neo4j_client.is_connected():
            services["neo4j"] = "connected"
        else:
            neo4j_client.verify_connectivity()
            services["neo4j"] = "connected"
    except Exception as e:
        services["neo4j"] = f"disconnected: {str(e)[:50]}"

    try:
        from app.storage.milvus_client import milvus_client
        if milvus_client.is_connected():
            services["milvus"] = "connected"
        else:
            milvus_client.list_collections()
            services["milvus"] = "connected"
    except Exception as e:
        services["milvus"] = f"disconnected: {str(e)[:50]}"

    try:
        from app.integrations.cache import cache_service
        if cache_service.ping():
            services["redis"] = "connected"
        else:
            services["redis"] = "disconnected"
    except Exception as e:
        services["redis"] = f"disconnected: {str(e)[:50]}"

    all_healthy = all(v == "connected" for v in services.values())

    return ApiResponse(
        data={
            "status": "healthy" if all_healthy else "degraded",
            "version": settings.VERSION,
            "services": services,
        }
    )
