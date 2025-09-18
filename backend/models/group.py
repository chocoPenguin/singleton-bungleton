from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from pydantic import BaseModel
from typing import Optional

# SQLAlchemy ORM model
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    language = Column(String(10), nullable=False, default="ko")
    memo = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)
    author = relationship("Author", back_populates="groups")


# Pydantic models (DTO)
class GroupCreate(BaseModel):
    name: str
    language: str = "ko"
    memo: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    language: Optional[str] = None
    memo: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None

class GroupResponse(BaseModel):
    id: int
    name: str
    language: str
    memo: Optional[str] = None
    description: Optional[str] = None
    author_id: Optional[int] = None

    class Config:
        from_attributes = True