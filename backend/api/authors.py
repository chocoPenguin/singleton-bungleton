from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.author import Author, AuthorCreate, AuthorResponse

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: author creation
@router.post("/", response_model=AuthorResponse)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return AuthorResponse.from_orm(db_author)


# READ: retrieve all authors
@router.get("/", response_model=list[AuthorResponse])
def list_authors(db: Session = Depends(get_db)):
    db_authors = db.query(Author).all()
    return [AuthorResponse.from_orm(a) for a in db_authors]


# READ: retrieve single author
@router.get("/{author_id}", response_model=AuthorResponse)
def get_author(author_id: int, db: Session = Depends(get_db)):
    db_author = db.query(Author).filter(Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")
    return AuthorResponse.from_orm(db_author)


# DELETE: author deletion
@router.delete("/{author_id}")
def delete_author(author_id: int, db: Session = Depends(get_db)):
    db_author = db.query(Author).filter(Author.id == author_id).first()
    if not db_author:
        raise HTTPException(status_code=404, detail="Author not found")

    db.delete(db_author)
    db.commit()
    return {"message": f"출제자 {author_id} 삭제 완료"}