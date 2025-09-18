from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.question import Question, QuestionCreate, QuestionResponse
import json

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: create new question
@router.post("/", response_model=QuestionResponse)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    db_question = Question(
        resource_id=question.resource_id,
        question=question.question,
        choices=json.dumps(question.choices, ensure_ascii=False),  # store as JSON string
        answer=question.answer,
        max_score=question.max_score,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return QuestionResponse(
        id=db_question.id,
        resource_id=db_question.resource_id,
        question=db_question.question,
        choices=json.loads(db_question.choices),
        answer=db_question.answer,
    )


# READ: question list
@router.get("/", response_model=list[QuestionResponse])
def list_questions(db: Session = Depends(get_db)):
    db_questions = db.query(Question).all()
    return [
        QuestionResponse(
            id=q.id,
            resource_id=q.resource_id,
            type=q.type,  # 추가
            question=q.question,
            choices=json.loads(q.choices) if q.choices else [],
            max_score=q.max_score
        )
        for q in db_questions
    ]


# READ: single question
@router.get("/{question_id}", response_model=QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    return QuestionResponse(
        id=db_question.id,
        resource_id=db_question.resource_id,
        question=db_question.question,
        choices=json.loads(db_question.choices),
        answer=db_question.answer,
    )


# DELETE: delete question
@router.delete("/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(db_question)
    db.commit()
    return {"message": f"Question {question_id} has been deleted"}