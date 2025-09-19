from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from models.resource import Resource, ResourceCreate, ResourceUpdate, ResourceResponse
from database import SessionLocal
from services.resource_service import save_file, delete_file

router = APIRouter()

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE: create new resource
@router.post("/", response_model=ResourceResponse)
def create_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    db_resource = Resource(
        name=resource.name,
        resource_type=resource.resource_type,
        connection_key=resource.connection_key,
        description=resource.description,
        file_path=resource.file_path,
        content=resource.content,
        author_id=resource.author_id,
        type=resource.type
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.model_validate(db_resource)


# READ: retrieve all resources
@router.get("/", response_model=list[ResourceResponse])
def list_resources(db: Session = Depends(get_db)):
    db_resources = db.query(Resource).all()
    return [ResourceResponse.model_validate(r) for r in db_resources]


# READ: retrieve resources by author
@router.get("/author/{author_id}", response_model=list[ResourceResponse])
def get_resources_by_author(author_id: int, db: Session = Depends(get_db)):
    db_resources = db.query(Resource).filter(Resource.author_id == author_id).all()
    return [ResourceResponse.model_validate(r) for r in db_resources]


# READ: retrieve single resource
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse.model_validate(db_resource)


# UPDATE: modify resource
@router.put("/{resource_id}", response_model=ResourceResponse)
def update_resource(resource_id: int, resource: ResourceUpdate, db: Session = Depends(get_db)):
    db_resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not db_resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if resource.name is not None:
        db_resource.name = resource.name
    if resource.resource_type is not None:
        db_resource.resource_type = resource.resource_type
    if resource.connection_key is not None:
        db_resource.connection_key = resource.connection_key
    if resource.description is not None:
        db_resource.description = resource.description
    if resource.file_path is not None:
        db_resource.file_path = resource.file_path
    if resource.content is not None:
        db_resource.content = resource.content
    if resource.author_id is not None:
        db_resource.author_id = resource.author_id
    if resource.type is not None:
        db_resource.type = resource.type

    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.model_validate(db_resource)


# DELETE: delete resource
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


# Legacy endpoints for backwards compatibility
# upload resource (text based)
@router.post("/text", response_model=ResourceResponse)
def upload_text_resource(resource: ResourceCreate, db: Session = Depends(get_db)):
    resource.type = "text"
    return create_resource(resource, db)

# upload resource (file based)
@router.post("/file", response_model=ResourceResponse)
def upload_file_resource(
    name: str = Form(...),
    resource_type: str = Form(...),
    connection_key: str = Form(...),
    description: str = Form(None),
    author_id: int = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = save_file(file, author_id or 0)

    db_resource = Resource(
        name=name,
        resource_type=resource_type,
        connection_key=connection_key,
        description=description,
        file_path=file_path,
        author_id=author_id,
        type="file"
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return ResourceResponse.model_validate(db_resource)