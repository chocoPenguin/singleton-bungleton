from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.group import Group, GroupCreate, GroupUpdate, GroupResponse

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: create new group
@router.post("/", response_model=GroupResponse)
def create_group(group: GroupCreate, db: Session = Depends(get_db)):
    db_group = Group(
        name=group.name,
        language=group.language,
        memo=group.memo
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return GroupResponse.from_orm(db_group)


# READ: retrieve all groups
@router.get("/", response_model=list[GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    db_groups = db.query(Group).all()
    return [GroupResponse.from_orm(g) for g in db_groups]


# READ: retrieve single group
@router.get("/{group_id}", response_model=GroupResponse)
def get_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return GroupResponse.from_orm(db_group)


# UPDATE: modify group
@router.put("/{group_id}", response_model=GroupResponse)
def update_group(group_id: int, group: GroupUpdate, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.name is not None:
        db_group.name = group.name
    if group.language is not None:
        db_group.language = group.language
    if group.memo is not None:
        db_group.memo = group.memo

    db.commit()
    db.refresh(db_group)
    return GroupResponse.from_orm(db_group)


# DELETE: delete group
@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    db.delete(db_group)
    db.commit()
    return {"message": f"Group {group_id} has been deleted"}