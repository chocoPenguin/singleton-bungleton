from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

# SQLAlchemy ORM model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    language = Column(String(10), nullable=True)  # optional
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relation: group <-> users
    group = relationship("Group", backref="users")


# Pydantic DTO
class UserCreate(BaseModel):
    group_id: int
    name: str
    email: EmailStr
    language: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    group_id: int
    name: str
    email: EmailStr
    language: Optional[str] = None

    class Config:
        from_attributes = True