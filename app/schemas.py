from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from .models import JobStatus


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

    model_config = {"from_attributes": True}


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
    csv_data: List[CSVDataOut] = []  # Nested rows

    model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
    job_id: int
    status: JobStatus
    message: str


class UserBase(BaseModel):
    """
    Basic User model fields and their types
    """

    email: str
    username: str


class UserCreate(UserBase):
    """
    Data validation class for user creation or retrieve.
    """

    password: str


class UserResponse(UserBase):
    """
    Schema class for user response
    """

    id: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    """
    Schema for user login.
    """

    email: str
    password: str


class Token(BaseModel):
    """
    Token field datatype config.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    TokenData configuration of field
    """
    email: str | None = None
    username: str | None = None
