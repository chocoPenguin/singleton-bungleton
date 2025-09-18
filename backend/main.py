from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, groups, questions, resources, users, authors, question_sets, question_assignments
from database import engine, Base
from models import Group, Resource

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Qraft",
    description="Qraft (가칭)",
    version="0.1.0",
)

# CORS 설정 (Vue와 연동을 위해 필수!) - 라우터 등록 전에 먼저 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(authors.router, prefix="/api/authors", tags=["Authors"])
app.include_router(groups.router, prefix="/api/groups", tags=["Groups"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(question_sets.router, prefix="/api/question_sets", tags=["QuestionSets"])
app.include_router(question_assignments.router, prefix="/api/question_assignments", tags=["QuestionAssignments"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Education AI Service API"}

@app.post("/api/chat")
def chat(data: dict):
    # 나중에 OpenAI API 호출 로직
    message = data.get("message", "")
    return {"response": f"AI: {message}에 대한 답변입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)