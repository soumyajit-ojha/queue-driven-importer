from celery import Celery
from decouple import config


celery = Celery(
    "csv_worker",
    broker=config("CELERY_BROKER_URL"),
    backend=config("CELERY_RESULT_BACKEND")
)

celery.conf.update(
    task_track_started=True,
    result_expires=3600,
)
# celery.conf.worker_pool = "eventlet"
# celery.conf.worker_concurrency = 10

celery.autodiscover_tasks(['app'])

# celery.conf.broker_url = config("CELERY_BROKER_URL")
# celery.conf.result_backend = config("CELERY_RESULT_BACKEND")
