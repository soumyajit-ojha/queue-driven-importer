import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class UploadCSV(Base):
    __tablename__ = "upload_jobs"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(100), nullable=False)
    original_filename = Column(String(100), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    csv_data = relationship("CSVData", back_populates="upload_csv")


class CSVData(Base):
    __tablename__ = "csv_data"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("upload_jobs.id"), index=True)
    # Example: we store specific columns as text; you can adapt to your schema.
    name = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    loc = Column(String(100), nullable=True)
    extra = Column(String(100), nullable=True)

    upload_csv = relationship("UploadCSV", back_populates="csv_data")
