from celery import Celery

celery_client = Celery(
    "rag_api",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0",
)

celery_client.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_client.conf.task_routes = {
    "app.tasks.*": {"queue": "default"},
}
