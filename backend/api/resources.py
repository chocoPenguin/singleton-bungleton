from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from models.resource import Resource, ResourceCreate, ResourceResponse
from database import SessionLocal
from services.resource_service import save_file, delete_file

router = APIRouter()

# Database session dependency (stub for example)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# upload resource (text based)
@router.post("/text", response_model=ResourceResponse)
def upload_text_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = Resource(
        group_id=resource.group_id,
        type="text",
        content=resource.content
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.from_orm(db_resource)

# upload resource (file based)
@router.post("/file", response_model=ResourceResponse)
def upload_file_resource(group_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = save_file(file, group_id)

    db_resource = Resource(
        group_id=group_id,
        type="file",
        file_path=file_path
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.from_orm(db_resource)

# retrieve resource
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse.from_orm(db_resource)

@router.get("/", response_model=list[ResourceResponse])
def list_resources(db: Session = Depends(get_db)):
    db_resources = db.query(Resource).all()
    return [ResourceResponse.from_orm(r) for r in db_resources]

# delete resource
@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # if file based, delete the file as well
    if db_resource.type == "file" and db_resource.file_path:
        delete_file(db_resource.file_path)

    db.delete(db_resource)
    db.commit()
    return {"message": f"Resource {resource_id} has been deleted"}