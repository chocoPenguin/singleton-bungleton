from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.question_assignment import QuestionAssignment, QuestionAssignmentCreate, QuestionAssignmentResponse
from models.question import Question, QuestionResponse
from services.feedback_service import get_feedback_service
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import json

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: question assignment creation
@router.post("/", response_model=QuestionAssignmentResponse)
def create_assignment(assign: QuestionAssignmentCreate, db: Session = Depends(get_db)):
    db_assign = QuestionAssignment(**assign.dict())
    db.add(db_assign)
    db.commit()
    db.refresh(db_assign)
    return QuestionAssignmentResponse.from_orm(db_assign)


# READ: question assignment list
@router.get("/", response_model=list[QuestionAssignmentResponse])
def list_assignments(db: Session = Depends(get_db)):
    db_assignments = db.query(QuestionAssignment).all()
    return [QuestionAssignmentResponse.from_orm(a) for a in db_assignments]


# READ: question assignment detail
@router.get("/{assign_id}", response_model=QuestionAssignmentResponse)
def get_assignment(assign_id: int, db: Session = Depends(get_db)):
    db_assign = db.query(QuestionAssignment).filter(QuestionAssignment.id == assign_id).first()
    if not db_assign:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return QuestionAssignmentResponse.from_orm(db_assign)


# DELETE: question assignment deletion
@router.delete("/{assign_id}")
def delete_assignment(assign_id: int, db: Session = Depends(get_db)):
    db_assign = db.query(QuestionAssignment).filter(QuestionAssignment.id == assign_id).first()
    if not db_assign:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(db_assign)
    db.commit()
    return {"message": f"Question assignment {assign_id} has been deleted"}

# READ: question with question assignment
@router.get("/quiz/list", response_model=List[QuestionResponse])
def get_assignment_with_questions(
    user_id: Optional[int] = None,
    question_set_id: Optional[int] = None,
    db: Session = Depends(get_db)):

    # JOIN 쿼리 작성
    query = db.query(QuestionAssignment, Question).join(
      Question, QuestionAssignment.question_id == Question.id
    )

    # 필터 조건 추가
    if user_id:
      query = query.filter(QuestionAssignment.user_id == user_id)
    if question_set_id:
      query = query.filter(QuestionAssignment.question_set_id == question_set_id)

    results = query.all()
    print(results)
    return [
      QuestionResponse(
          id=q[1].id,
          resource_id=q[1].resource_id if q[1].resource_id else 0,
          type=q[1].type,  # 추가
          question=q[1].question,
          choices=json.loads(q[1].choices) if q[1].choices else [],
          max_score=q[1].max_score
      )
      for q in results
    ]

# Pydantic models for quiz feedback
class FeedbackRequest(BaseModel):
    answers: Dict[str, Any]

@router.post("/quiz/submit")
async def process_quiz_result(request: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Generate quiz using Microsoft Copilot Studio AI Agent
    """
    try:
        print(request)
        feedback_service = get_feedback_service(db)

        result = await feedback_service.generate_feedback_from_ai(
            answer=request.answers
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate quiz")
            )

#         return {
#             "message": "Quiz generated successfully",
#             "question_set_id": result["question_set_id"],
#             "questions_created": result["questions_created"],
#             "data": result["data"]
#        }

    except Exception as e:
       import traceback
       print(f"Generate feedback error: {str(e)}")
       print(f"Traceback: {traceback.format_exc()}")
       raise HTTPException(
           status_code=500,
           detail=f"Internal server error: {str(e)}"
       )