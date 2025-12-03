from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    csv_data = relationship(
        "CSVData", back_populates="user", cascade="all, delete-orphan"
    )


class CSVData(Base):
    __tablename__ = "csv_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(150), nullable=False)
    total_row = Column(Integer, nullable=True)
    data = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="items")
