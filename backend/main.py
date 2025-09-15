from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Education AI Service")

# CORS 설정 (Vue와 연동을 위해 필수!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue 개발서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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