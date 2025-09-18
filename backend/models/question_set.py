from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
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
    num_questions = Column(Integer, nullable=True)                            # number of quiz questions
    language = Column(String(50), nullable=True)                              # language
    difficulty = Column(String(50), nullable=True)                            # difficulty
    title = Column(String(255), nullable=True)                                # quiz set title
    description = Column(Text, nullable=True)                                 # quiz requirements (instructions)
    expires_at = Column(DateTime, nullable=True)                              # expiration datetime
    created_at = Column(DateTime, default=datetime.utcnow)

    # ORM relationships
    assignments = relationship("QuestionAssignment", backref="question_set", cascade="all, delete")
    group = relationship("Group", backref="question_sets")
    author = relationship("Author", backref="question_sets")
    resource = relationship("Resource", backref="question_sets")
    user = relationship("User", backref="question_sets")


# Pydantic DTO
class QuestionSetCreate(BaseModel):
    author_id: int
    resource_id: Optional[int] = None
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    num_questions: Optional[int] = None
    language: Optional[str] = None
    difficulty: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None

class QuestionSetResponse(BaseModel):
    id: int
    author_id: int
    resource_id: Optional[int] = None
    group_id: Optional[int] = None
    user_id: Optional[int] = None
    num_questions: Optional[int] = None
    language: Optional[str] = None
    difficulty: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    # Relationship fields
    author: Optional['AuthorResponse'] = None
    group: Optional['GroupResponse'] = None
    resource: Optional['ResourceResponse'] = None

    # Add a field to hold the total number of users
    total_users: int = 0

    class Config:
        from_attributes = True


# Response models for relationships
class AuthorResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class GroupResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ResourceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True