from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.question_set import QuestionSet, QuestionSetCreate
from models.question import Question, QuestionCreate
from models.question_assignment import QuestionAssignment, QuestionAssignmentCreate
from models.group import Group
from models.user import User
from services.azure_ai_foundry_service import QuizFeedbackService
import json


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_feedback_from_ai(
        self,
        answer: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate quiz using AI agent and save to database
        """
        try:
            # Call AI Foundry agent to generate quiz following ai-foundry-agent.md
            async with QuizFeedbackService() as ai_service:
                feedback_data = await ai_service.generate_feedback(answer)

                # Validate AI response
                if "error" in feedback_data:
                    return {"success": False, "error": feedback_data["error"]}

                return {
                    "success": True,
                    "message": "피드백이 성공적으로 생성되었습니다.",
                    "feedback": feedback_data,
                    "answers_processed": answer
                }

        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _save_feedback_to_db(
        self,
        quiz_data: Dict[str, Any],
        group_id: int,
        author_id: int,
        resource_id: Optional[int],
        num_questions: int,
        language: str,
        difficulty: str,
        description: str,
        users_in_group: List[User]
    ) -> Dict[str, Any]:
        """
        Save AI-generated quiz to database with proper question assignments
        """
        try:
            # 1. Create QuestionSet first
            question_set_data = QuestionSetCreate(
                author_id=author_id,
                resource_id=resource_id,
                group_id=group_id,
                user_id=None,  # Group-based quiz
                num_questions=num_questions,
                language=language,
                difficulty=difficulty,
                description=description
            )

            db_question_set = QuestionSet(**question_set_data.model_dump())
            self.db.add(db_question_set)
            self.db.flush()  # Get the question_set ID without committing

            created_questions = []
            created_assignments = []
            total_questions = quiz_data["questions"]

            # 2. Create Questions and Assignments
            for i, question_data in enumerate(total_questions):
                # Create Question
                db_question = Question(
                    resource_id=resource_id,  # Allow None
                    author_id=author_id,
                    type='M',  # Multiple choice
                    question=question_data["question"],
                    choices=json.dumps(question_data["choices"]),
                    answer=question_data["answer"],
                    max_score=10  # Default score
                )
                self.db.add(db_question)
                self.db.flush()  # Get the question ID
                created_questions.append(db_question)

                # 3. Create Question Assignments for each user in the group
                # Distribute questions evenly among users
                for j, user in enumerate(users_in_group):
                    # Each user gets different questions (round-robin distribution)
                    if i % len(users_in_group) == j:
                        assignment = QuestionAssignment(
                            question_set_id=db_question_set.id,
                            question_id=db_question.id,
                            group_id=group_id,
                            user_id=user.id,
                            user_answer=None,  # None initially
                            user_score=None,   # None initially
                            status="assigned"
                        )
                        self.db.add(assignment)
                        created_assignments.append(assignment)

            # Return success response
            return {
                "success": True,
                "question_set_id": db_question_set.id,
                "questions_created": len(created_questions),
                "assignments_created": len(created_assignments),
                "total_users": len(users_in_group),
                "questions_per_user": num_questions,
                "data": {
                    "question_set": {
                        "id": db_question_set.id,
                        "group_id": group_id,
                        "num_questions": num_questions,
                        "description": description
                    },
                    "generated_questions": [
                        {
                            "id": q.id,
                            "question": q.question,
                            "choices": json.loads(q.choices),
                            "answer": q.answer
                        } for q in created_questions
                    ]
                }
            }

        except Exception as e:
            import traceback
            print(f"Quiz service save error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            self.db.rollback()
            return {
                "success": False,
                "error": f"Error saving quiz: {str(e)}"
            }


def get_feedback_service(db: Session) -> FeedbackService:
    """
    Factory function to create FeedbackService instance
    """
    return FeedbackService(db)