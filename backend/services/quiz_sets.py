from crud.dataverse_sync import send_to_dataverse
from models import QuestionAssignment
from database import SessionLocal

def sync_question_assignments_to_dataverse():
    from models.user import User

    db = SessionLocal()
    try:
        # 유저별 문제집 쌍 추출
        results = db.query(
            QuestionAssignment.user_id,
            QuestionAssignment.question_set_id
        ).distinct().all()

        for user_id, question_set_id in results:
            # 사용자 정보 조회
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"[WARNING] User {user_id} not found, skipping dataverse sync")
                continue

            email = user.email
            link = f"http://localhost:5173/quiz/list?user_id={user_id}&question_set_id={question_set_id}"

            print(f"[DEBUG] Syncing user {user_id}: email={email}, link={link}")
            send_to_dataverse(user_id, question_set_id, email, link)
    finally:
        db.close()