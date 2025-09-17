from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# SQLAlchemy ORM model
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)  # link to Resource
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)  # link to Author
    question = Column(Text, nullable=False)
    choices = Column(Text, nullable=False)  # save JSON as string
    answer = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationship
    resource = relationship("Resource", backref="questions")


# Pydantic DTO
class QuestionCreate(BaseModel):
    resource_id: int
    question: str
    choices: List[str]
    answer: str
    author_id: Optional[int] = None

class QuestionResponse(BaseModel):
    id: int
    resource_id: int
    question: str
    choices: List[str]
    answer: str
    author_id: Optional[int] = None

    class Config:
        from_attributes = True