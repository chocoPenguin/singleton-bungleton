from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class QuestionAssignment(Base):
    __tablename__ = "question_assignments"

    id = Column(Integer, primary_key=True, index=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)   # Group
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)     # User
    user_answer = Column(Text, nullable=False)
    user_score = Column(Integer, nullable=False)
    status = Column(String(20), default="assigned")  # status: assigned, completed, etc.
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic DTO
class QuestionAssignmentCreate(BaseModel):
    question_set_id: int
    question_id: int
    group_id: Optional[int] = None
    user_id: Optional[int] = None

class QuestionAssignmentResponse(BaseModel):
    id: int
    question_set_id: int
    question_id: int
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    status: str

    class Config:
        from_attributes = True