from celery import Celery
from decouple import config


# Optional Redis – if not provided, Celery falls back to in-memory backend
BROKER_URL = config("CELERY_BROKER_URL", default="memory://")
RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="cache+memory://")

celery = Celery(
    "csv_worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

celery.conf.update(
    task_track_started=True,
    result_expires=3600,
    # Make Celery optional if running without broker/backend
    task_always_eager=(
        BROKER_URL == "memory://" and RESULT_BACKEND == "cache+memory://"
    ),
)
# celery.conf.worker_pool = "eventlet"
# celery.conf.worker_concurrency = 10

celery.autodiscover_tasks(["app"])

# celery.conf.broker_url = config("CELERY_BROKER_URL")
# celery.conf.result_backend = config("CELERY_RESULT_BACKEND")
