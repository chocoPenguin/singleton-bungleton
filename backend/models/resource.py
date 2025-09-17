from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
from typing import Optional
from datetime import datetime


# SQLAlchemy ORM
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, index=True)
    type = Column(String(50))                       # "text" or "file"
    file_path = Column(String(255), nullable=True)  # file path
    content = Column(Text, nullable=True)           # text resource
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class ResourceCreate(BaseModel):
    group_id: int
    content: Optional[str] = None  # text based only

class ResourceResponse(BaseModel):
    id: int
    group_id: int
    type: str
    content: Optional[str] = None
    file_path: Optional[str] = None