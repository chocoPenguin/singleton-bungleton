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
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationships
    groups = relationship("Group", backref="owner")          # Author → Groups
    questions = relationship("Question", backref="author")   # Author → Questions


# Pydantic DTO
class AuthorCreate(BaseModel):
    name: str
    email: EmailStr

class AuthorResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True