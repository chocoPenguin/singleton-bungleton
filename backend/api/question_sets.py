from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.question_set import QuestionSet, QuestionSetCreate, QuestionSetResponse
from services.quiz_service import get_quiz_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: question set creation
@router.post("/", response_model=QuestionSetResponse)
def create_question_set(qs: QuestionSetCreate, db: Session = Depends(get_db)):
    db_qs = QuestionSet(**qs.model_dump())
    db.add(db_qs)
    db.commit()
    db.refresh(db_qs)
    return QuestionSetResponse.model_validate(db_qs)


# READ: question set list
@router.get("/", response_model=list[QuestionSetResponse])
def list_question_sets(db: Session = Depends(get_db)):
    from models.group import Group
    from models.user import User
    from sqlalchemy.orm import joinedload

    # Load question sets with related group information
    db_qs_list = (
        db.query(QuestionSet)
        .options(
            joinedload(QuestionSet.group).joinedload(Group.users),
            joinedload(QuestionSet.author),
            joinedload(QuestionSet.resource),
        )
        .all()
    )

    result = []
    for qs in db_qs_list:
        # Convert to response model and add calculated fields
        qs_response = QuestionSetResponse.model_validate(qs)
        qs_response.total_users = len(qs.group.users) if qs.group else 0
        result.append(qs_response)

    return result


# READ: single question set
@router.get("/{qs_id}", response_model=QuestionSetResponse)
def get_question_set(qs_id: int, db: Session = Depends(get_db)):
    db_qs = db.query(QuestionSet).filter(QuestionSet.id == qs_id).first()
    if not db_qs:
        raise HTTPException(status_code=404, detail="QuestionSet not found")
    return QuestionSetResponse.model_validate(db_qs)


# READ: get question set with detailed questions and assignments
@router.get("/{qs_id}/details")
def get_question_set_details(qs_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a question set including questions and assignments
    """
    from models.question import Question
    from models.question_assignment import QuestionAssignment
    import json

    # Get question set
    db_qs = db.query(QuestionSet).filter(QuestionSet.id == qs_id).first()
    if not db_qs:
        raise HTTPException(status_code=404, detail="QuestionSet not found")

    # Get assignments for this question set
    assignments = (
        db.query(QuestionAssignment)
        .filter(QuestionAssignment.question_set_id == qs_id)
        .all()
    )

    # Get detailed questions with assignment info
    question_details = []
    for assignment in assignments:
        question = (
            db.query(Question)
            .filter(Question.id == assignment.question_id)
            .first()
        )

        if question:
            question_details.append({
                "assignment_id": assignment.id,
                "question_id": question.id,
                "question": question.question,
                "choices": json.loads(question.choices) if question.choices else [],
                "answer": question.answer,
                "type": question.type,
                "max_score": question.max_score,
                "user_id": assignment.user_id,
                "user_answer": assignment.user_answer,
                "user_score": assignment.user_score,
                "status": assignment.status,
                "group_id": assignment.group_id
            })

    return {
        "question_set": QuestionSetResponse.model_validate(db_qs),
        "questions": question_details,
        "total_questions": len(question_details)
    }


# DELETE: question set deletion
@router.delete("/{qs_id}")
def delete_question_set(qs_id: int, db: Session = Depends(get_db)):
    db_qs = db.query(QuestionSet).filter(QuestionSet.id == qs_id).first()
    if not db_qs:
        raise HTTPException(status_code=404, detail="QuestionSet not found")
    db.delete(db_qs)
    db.commit()
    return {"message": f"Question set {qs_id} has been deleted"}


# Pydantic models for quiz generation
class QuizGenerateRequest(BaseModel):
    group_id: int
    author_id: int
    num_questions: int
    description: str
    resource_id: Optional[int] = None


# GENERATE: AI-powered quiz generation
@router.post("/generate")
async def generate_quiz(request: QuizGenerateRequest, db: Session = Depends(get_db)):
    """
    Generate quiz using Microsoft Copilot Studio AI Agent
    """
    try:
        quiz_service = get_quiz_service(db)

        result = await quiz_service.generate_quiz_from_ai(
            group_id=request.group_id,
            num_questions=request.num_questions,
            description=request.description,
            author_id=request.author_id,
            resource_id=request.resource_id
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to generate quiz")
            )

        return {
            "message": "Quiz generated successfully",
            "question_set_id": result["question_set_id"],
            "questions_created": result["questions_created"],
            "data": result["data"]
        }

    except Exception as e:
        import traceback
        print(f"Generate quiz error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# READ: Get quizzes by group
@router.get("/by-group/{group_id}")
def get_quizzes_by_group(group_id: int, db: Session = Depends(get_db)):
    """
    Get all quizzes for a specific group
    """
    try:
        quiz_service = get_quiz_service(db)
        result = quiz_service.get_quiz_by_group(group_id)

        if isinstance(result, dict) and "error" in result:
            raise HTTPException(
                status_code=500,
                detail=result["error"]
            )

        return {
            "group_id": group_id,
            "quizzes": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving quizzes: {str(e)}"
        )