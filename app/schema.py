from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        orm_mode = True


class DataImportTaskCreate(BaseModel):
    user_id: int
    filename: str
    task_id: str


class DataImportTaskOut(BaseModel):
    id: int
    user_id: int
    task_id: str
    filename: str
    status: str
    row_count: Optional[int]
    error: Optional[str]
    created_at: Optional[datetime]
    finished_at: Optional[datetime]

    class Config:
        orm_mode = True
