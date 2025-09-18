from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User, UserCreate, UserResponse
from models.author import Author, AuthorResponse
from security import get_current_user

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: create new user
@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.from_orm(db_user)


# READ: retrieve all users
@router.get("/group/{group_id}", response_model=list[UserResponse])
def list_users_by_group(group_id: int, db: Session = Depends(get_db)):
    db_users = db.query(User).filter(User.group_id == group_id).all()
    return [UserResponse.from_orm(u) for u in db_users]


# READ: get current user info
@router.get("/me", response_model=AuthorResponse)
def get_current_user_info(current_user: Author = Depends(get_current_user)):
    return AuthorResponse.from_orm(current_user)


# READ: retrieve single user
@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.from_orm(db_user)


# DELETE: delete user
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"유저 {user_id} 삭제 완료"}