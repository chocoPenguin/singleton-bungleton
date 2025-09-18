from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

# SQLAlchemy ORM model
class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)        # login
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationships
    groups = relationship("Group", back_populates="author")  # Author → Groups


# Pydantic DTO
class AuthorCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class AuthorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True