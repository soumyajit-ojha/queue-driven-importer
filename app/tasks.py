from celery.utils.log import get_task_logger
from app.celery import celery
from .database import SyncSessionLocal
from .models import UploadCSV, CSVData, JobStatus
from .utils import read_csv_as_dicts, delete_file_safe

logger = get_task_logger(__name__)


@celery.task(
    name="app.tasks.process_csv_task",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def process_csv_task(self, job_id: int, file_path: str):
    """
    Synchronous Celery Task.
    No asyncio.run(), no await.
    """
    logger.info(f"[TASK STARTED] job_id={job_id}")

    # 1. CALCULATE DELAY LOGIC
    delay_seconds = calculate_delay(file_path)
    logger.info(f"[DELAY] Sleeping for {delay_seconds} seconds...")

    # 2. PROCESS DATABASE (Synchronously)
    # We use a context manager to ensure the session closes
    session = SyncSessionLocal()

    try:
        # Fetch Job
        job = session.get(UploadCSV, job_id)
        if not job:
            logger.error(f"Job {job_id} not found.")
            return

        # Update Status to PROCESSING
        job.status = JobStatus.PROCESSING
        session.commit()

        # Insert CSV Data
        # Re-open file to read data (since we might have read it for counting)
        bulk_data = []
        for row in read_csv_as_dicts(file_path, delay=delay_seconds):
            csv_obj = CSVData(
                job_id=job_id,
                name=row.get("name"),
                role=row.get("role"),
                loc=row.get("location"),
                extra=row.get("extra_info"),
            )
            bulk_data.append(csv_obj)

        # Bulk save is faster
        session.add_all(bulk_data)
        session.commit()

        # Update Status to SUCCESS
        job.status = JobStatus.SUCCESS
        job.error_message = None
        session.commit()

        logger.info(
            f"[TASK SUCCESS] job_id={job_id} processed {len(bulk_data)} rows."
        )
        delete_file_safe(file_path)

    except Exception as e:
        session.rollback()
        # If job object exists, mark failed
        if "job" in locals() and job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            session.commit()

        logger.error(f"[TASK FAILED] {e}")
        raise e
    finally:
        session.close()  # Always close sync sessions manually or via context manager



def calculate_delay(file_path: str) -> int:
    """
    Logic:
    Time = N // 4
    If N < 20 -> 4 sec
    If N > 100 -> 17 sec
    """
    line_count = 0

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Efficiently count lines
            line_count = sum(1 for _ in f)
            # Subtract 1 for header if your CSV has headers
            if line_count > 0:
                line_count -= 1
    except Exception:
        line_count = 0

    calculated_time = line_count // 2

    if line_count < 20:
        return 10
    elif line_count > 100:
        return 40
    else:
        return calculated_time
