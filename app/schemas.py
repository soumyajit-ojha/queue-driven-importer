from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .models import JobStatus


"""
CSVData Schemas
"""

class CSVDataBase(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    loc: Optional[str] = None
    extra: Optional[str] = None


class CSVDataCreate(CSVDataBase):
    """For worker insertion (usually not called by client directly)"""
    job_id: int


class CSVDataOut(CSVDataBase):
    """Response schema for retrieved CSV rows"""
    id: int

    model_config = {
        "from_attributes": True
    }



"""
UploadCSV (Job) Schemas
"""

class UploadCSVBase(BaseModel):
    original_filename: str
    status: JobStatus
    error_message: Optional[str] = None


class UploadCSVCreate(BaseModel):
    """Schema when new upload job is created internally by API"""
    original_filename: str
    file_path: str


class UploadCSVOut(UploadCSVBase):
    """Job details API response"""
    id: int
    file_path: str
    created_at: datetime
    updated_at: datetime
    csv_data: List[CSVDataOut] = []    # Nested rows

    model_config = {
        "from_attributes": True
    }



"""
Upload response when file uploaded
"""

class UploadResponse(BaseModel):
    job_id: int
    status: JobStatus
    message: str
