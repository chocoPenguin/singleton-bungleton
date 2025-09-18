from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Any

# SQLAlchemy ORM model
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)  # link to Resource
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=True)  # link to Author
    type = Column(String(1), nullable=False, default='M') # M: multiple_choices, S: short subjective, L: Long subjective
    question = Column(Text, nullable=False)
    choices = Column(Text, nullable=True)  # save JSON as string
    answer = Column(Text, nullable=False)
    max_score = Column(Integer, nullable=False, default=10)  # Score assigned to this question
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationship
    resource = relationship("Resource", backref="questions")


# Pydantic DTO
class QuestionCreate(BaseModel):
    resource_id: int
    type: str
    question: str
    choices: Optional[List[str]] = None
    answer: str
    max_score: int
    author_id: Optional[int] = None

class QuestionResponse(BaseModel):
    id: int
    resource_id: int
    type: str
    question: str
    choices: List[Any]
    max_score: int

    class Config:
        from_attributes = True