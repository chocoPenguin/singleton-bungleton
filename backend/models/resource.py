from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from database import Base
from typing import Optional
from datetime import datetime


# SQLAlchemy ORM
class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    resource_type = Column(String(10), nullable=False)  # SP, LS, GC, S3
    connection_key = Column(String(500), nullable=False)  # Agent ID, connection string, etc.
    description = Column(Text, nullable=True)  # For quiz generation prompts
    file_path = Column(String(255), nullable=True)  # Optional: for local files
    content = Column(Text, nullable=True)           # text resource
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    type = Column(String(50), default="external")   # "external", "file", "text"
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class ResourceCreate(BaseModel):
    name: str
    resource_type: str  # SP, LS, GC, S3
    connection_key: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    type: str = "external"

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    resource_type: Optional[str] = None
    connection_key: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    type: Optional[str] = None

class ResourceResponse(BaseModel):
    id: int
    name: str
    resource_type: str
    connection_key: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None
    author_id: Optional[int] = None
    type: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True