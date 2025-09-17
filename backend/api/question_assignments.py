from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.question_assignment import QuestionAssignment, QuestionAssignmentCreate, QuestionAssignmentResponse

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