from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
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

# READ: question with question assignment (결과 보기용)
@router.get("/quiz/result", response_model=List[Dict[str, Any]])
def get_quiz_results(
    user_id: Optional[int] = None,
    question_set_id: Optional[int] = None,
    db: Session = Depends(get_db)):

    # JOIN 쿼리 작성 (question_assignments 기본)
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

    # question_assignments 데이터 포함하여 반환
    return [
      {
          "id": q[1].id,
          "resource_id": q[1].resource_id if q[1].resource_id else 0,
          "type": q[1].type,
          "question": q[1].question,
          "choices": json.loads(q[1].choices) if q[1].choices else [],
          "max_score": q[1].max_score,
          # question_assignments 데이터 추가
          "assignment_id": q[0].id,
          "user_id": q[0].user_id,
          "question_set_id": q[0].question_set_id,
          "user_answer": q[0].user_answer,
          "user_score": q[0].user_score,
          "feedback": q[0].feedback,
          "status": q[0].status
      }
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

        # AI 결과에서 feedback 데이터만 추출
        feedback_data = result.get("feedback", {})
        update_question_assignment_scores(feedback_data, db)

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

# UPDATE: question assignment feedback and score
def update_question_assignment_scores(
    feedback_data: Dict[str, Dict[str, Any]],
    db: Session
) -> Dict[str, Any]:
    """
    Update question assignments with feedback, user scores, and user answers
    feedback_data format:
    {
        "question_id": {
            "user_score": score,
            "feedback": "feedback content",
            "user_answer": "user's answer"
        },
        "0": {  # ignored
            "user_score": total_score,
            "feedback": "overall feedback"
        }
    }
    """
    updated_count = 0
    failed_updates = []

    try:
        update_query = text("""
            UPDATE question_assignments
            SET feedback = :feedback, user_score = :user_score, user_answer = :user_answer, status = 'completed'
            WHERE question_id = :question_id
        """)

        for question_id_str, data in feedback_data.items():
            # question_id가 "0"인 경우 무시
            if question_id_str == "0":
                continue

            try:
                question_id = int(question_id_str)
                result = db.execute(update_query, {
                    "feedback": data.get("feedback", ""),
                    "user_score": data.get("user_score", 0),
                    "user_answer": data.get("user_answer", ""),
                    "question_id": question_id
                })

                if result.rowcount > 0:
                    updated_count += 1
                else:
                    failed_updates.append(question_id)

            except (ValueError, Exception) as e:
                print(f"Failed to update question {question_id_str}: {str(e)}")
                failed_updates.append(question_id_str)

        db.commit()

        return {
            "success": True,
            "updated_count": updated_count,
            "failed_updates": failed_updates
        }

    except Exception as e:
        db.rollback()
        print(f"Failed to update question assignments: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "updated_count": 0
        }
