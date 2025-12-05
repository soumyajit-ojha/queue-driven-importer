# app/main.py
import os
import uuid
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from contextlib import asynccontextmanager

from decouple import config
from .database import Base, engine, get_db
from .models import UploadCSV, JobStatus
from .schemas import UploadResponse, UploadCSVOut
from .tasks import process_csv_task
from .utils import delete_file_safe

UPLOAD_DIR = "./uploads"

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        print("\n✅ FastAPI Started | Upload Dir OK.\n")
    except Exception as e:
        print("error: Upload Dir\n".str(e))
        raise e
    yield
    await engine.dispose()
    # delete_file_safe(UPLOAD_DIR)
    print("❌ Database connection closed cleanly")


app = FastAPI(title="queue-driven-importer", lifespan=lifespan)


# 1) UPLOAD CSV → Create Job + Push Celery Task ✅✅✅ working
@app.post(
    "/upload",
    response_model=UploadResponse,
    status_code=202,
    summary="Upload CSV file for async background processing",
)
async def upload_csv(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are allowed")

    # Generate unique filename & save locally temporarily
    unique_name = f"{uuid.uuid4().hex}.csv"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    try:
        content = await file.read()
        with open(file_path, "wb") as fp:
            fp.write(content)
    except Exception as e:
        raise HTTPException(500, f"Failed to store file: {e}")

    # Create DB job entry
    job = UploadCSV(
        original_filename=file.filename, file_path=file_path, status=JobStatus.PENDING
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Call Celery task asynchronously
    process_csv_task.delay(job_id=job.id, file_path=file_path)

    return UploadResponse(
        job_id=job.id,
        status=job.status,
        message="Upload successful. Processing started in background.",
    )


# 2) FETCH JOB STATUS + CSV Results ❌❌❌error
@app.get(
    "/jobs/{job_id}",
    response_model=UploadCSVOut,
    summary="Get job status and processed CSV data",
)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    query = (
        select(UploadCSV)
        .options(selectinload(UploadCSV.csv_data))
        .where(UploadCSV.id == job_id)
    )
    # result = await db.execute(select(UploadCSV).where(UploadCSV.id == job_id))
    result = await db.execute(query)
    print("GET JOB", result)
    job = result.scalars().unique().first()

    if not job:
        raise HTTPException(404, "Job not found")

    return job


# Root
@app.get("/")
def root():
    return {"message": "CSV async processor is running 🚀"}
