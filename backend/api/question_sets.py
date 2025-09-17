from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.question_set import QuestionSet, QuestionSetCreate, QuestionSetResponse

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
    db_qs = QuestionSet(**qs.dict())
    db.add(db_qs)
    db.commit()
    db.refresh(db_qs)
    return QuestionSetResponse.from_orm(db_qs)


# READ: question set list
@router.get("/", response_model=list[QuestionSetResponse])
def list_question_sets(db: Session = Depends(get_db)):
    db_qs_list = db.query(QuestionSet).all()
    return [QuestionSetResponse.from_orm(qs) for qs in db_qs_list]


# READ: single question set
@router.get("/{qs_id}", response_model=QuestionSetResponse)
def get_question_set(qs_id: int, db: Session = Depends(get_db)):
    db_qs = db.query(QuestionSet).filter(QuestionSet.id == qs_id).first()
    if not db_qs:
        raise HTTPException(status_code=404, detail="QuestionSet not found")
    return QuestionSetResponse.from_orm(db_qs)


# DELETE: question set deletion
@router.delete("/{qs_id}")
def delete_question_set(qs_id: int, db: Session = Depends(get_db)):
    db_qs = db.query(QuestionSet).filter(QuestionSet.id == qs_id).first()
    if not db_qs:
        raise HTTPException(status_code=404, detail="QuestionSet not found")
    db.delete(db_qs)
    db.commit()
    return {"message": f"Question set {qs_id} has been deleted"}