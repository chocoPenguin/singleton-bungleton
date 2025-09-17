from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models.author import Author
from security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register")
def register(email: str, password: str, name: str, db: Session = Depends(get_db)):
    db_author = db.query(Author).filter(Author.email == email).first()
    if db_author:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = get_password_hash(password)
    new_author = Author(email=email, hashed_password=hashed_pw, name=name)
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return {"msg": "Author created", "email": new_author.email}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    author = db.query(Author).filter(Author.email == form_data.username).first()
    if not author or not verify_password(form_data.password, author.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token = create_access_token(
        data={"sub": author.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}