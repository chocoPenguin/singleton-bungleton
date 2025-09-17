from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class QuestionSet(Base):
    __tablename__ = "question_sets"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)  # resources
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)        # group
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)          # user
    expires_at = Column(DateTime, nullable=True)                              # expiration datetime
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationships
    assignments = relationship("QuestionAssignment", backref="question_set", cascade="all, delete")


# Pydantic DTO
class QuestionSetCreate(BaseModel):
    author_id: int
    resource_id: Optional[int] = None
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    expires_at: Optional[datetime] = None

class QuestionSetResponse(BaseModel):
    id: int
    author_id: int
    resource_id: Optional[int] = None
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True