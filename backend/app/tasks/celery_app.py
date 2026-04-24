from celery import Celery
from app.config.settings import settings

celery_app = Celery(
    "docai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_queues={
        "default": {
            "exchange": "default",
            "routing_key": "default",
        },
        "parsing": {
            "exchange": "parsing",
            "routing_key": "parsing",
        },
        "embedding": {
            "exchange": "embedding",
            "routing_key": "embedding",
        },
    },
    task_default_queue="default",
    task_routes={
        "app.tasks.document_tasks.process_document": {"queue": "parsing"},
        "app.tasks.document_tasks.parse_document": {"queue": "parsing"},
        "app.tasks.document_tasks.extract_info": {"queue": "default"},
        "app.tasks.embedding_tasks.generate_embeddings": {"queue": "embedding"},
    },
    worker_concurrency=4,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
