from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.question_set import QuestionSet, QuestionSetCreate
from models.question import Question, QuestionCreate
from models.question_assignment import QuestionAssignment, QuestionAssignmentCreate
from models.group import Group
from models.user import User
from services.azure_ai_foundry_service import AzureAIFoundryService
import json


class QuizService:
    def __init__(self, db: Session):
        self.db = db

    async def generate_quiz_from_ai(
        self,
        group_id: int,
        num_questions: int,
        language: str,
        difficulty: str,
        description: str,
        title: str, # Add title parameter here
        author_id: int,
        resource_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate quiz using AI agent and save to database
        """
        try:
            # Get group information
            group = self.db.query(Group).filter(Group.id == group_id).first()
            if not group:
                return {"success": False, "error": "Group not found"}

            # Get users in the group
            users_in_group = self.db.query(User).filter(User.group_id == group_id).all()
            user_count = len(users_in_group)
            print(f"[DEBUG] num_questions: {num_questions}, user_count: {user_count}") # Log added

            if user_count == 0:
                return {"success": False, "error": "No users found in the group"}

            # Calculate total questions needed (num_questions per user)
            total_questions_needed = num_questions * user_count

            # Call AI Foundry agent to generate quiz following ai-foundry-agent.md
            async with AzureAIFoundryService() as ai_service:
                # Add scoring instruction to the description
                scoring_instruction = f"각 문제의 난이도에 따라 점수를 적절히 배분하여 총 {num_questions}문제의 총점이 100점이 되도록 하세요. 각 문제의 점수를 'max_score' 필드에 포함해주세요."
                updated_description = f"{description}\n\n{scoring_instruction}"

                quiz_data = await ai_service.generate_quiz(
                    group=group,
                    num_questions=num_questions,
                    language=language,
                    difficulty=difficulty,
                    description=updated_description, # Use updated description
                    user_count=user_count
                )

                # Validate AI response
                if "error" in quiz_data:
                    return {"success": False, "error": quiz_data["error"]}

                if not ai_service.validate_quiz_response(quiz_data):
                    return {
                        "success": False,
                        "error": "Invalid quiz format from AI",
                        "raw_response": quiz_data
                    }

            # Save the AI generated quiz to database
            save_result = self._save_quiz_to_db(
                quiz_data=quiz_data,
                group_id=group_id,
                author_id=author_id,
                resource_id=resource_id,
                num_questions=num_questions,
                language=language,
                difficulty=difficulty,
                description=description,
                title=title, # Pass title here
                users_in_group=users_in_group
            )

            if not save_result["success"]:
                return save_result

            # Commit all changes
            self.db.commit()

            return save_result

        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

    def _save_quiz_to_db(
        self,
        quiz_data: Dict[str, Any],
        group_id: int,
        author_id: int,
        resource_id: Optional[int],
        num_questions: int,
        language: str,
        difficulty: str,
        description: str,
        title: str, # Add title parameter here
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
                description=description,
                title=title # Use the passed title directly
            )

            db_question_set = QuestionSet(**question_set_data.model_dump())
            self.db.add(db_question_set)
            self.db.flush()  # Get the question_set ID without committing

            created_questions = []
            created_assignments = []
            total_questions_from_ai = quiz_data["questions"]
            print(f"[DEBUG] AI returned {len(total_questions_from_ai)} questions.") # Log added

            # 2. Create Questions
            for question_data in total_questions_from_ai:
                question_type = question_data.get("type", "M")
                db_question = Question(
                    resource_id=resource_id,
                    author_id=author_id,
                    type=question_type,
                    question=question_data["question"],
                    choices=json.dumps(question_data["choices"]) if question_data.get("choices") else None,
                    answer=question_data["answer"],
                    max_score=question_data.get("max_score", 10) # Use AI provided score, default to 10
                )
                self.db.add(db_question)
                self.db.flush()
                created_questions.append(db_question)

            # 3. Create Question Assignments for each user, assigning num_questions to each user
            question_index = 0
            for user in users_in_group:
                for _ in range(num_questions): # 각 사용자에게 num_questions 만큼 할당
                    if question_index < len(created_questions):
                        db_question = created_questions[question_index]
                        assignment = QuestionAssignment(
                            question_set_id=db_question_set.id,
                            question_id=db_question.id,
                            group_id=group_id,
                            user_id=user.id,
                            user_answer=None,
                            user_score=None,
                            status="assigned"
                        )
                        self.db.add(assignment)
                        created_assignments.append(assignment)
                        question_index += 1
                    else:
                        # AI가 생성한 질문 수가 부족한 경우 (예외 처리 또는 경고)
                        print(f"[WARNING] Not enough questions generated by AI for user {user.id}. Expected {num_questions}, but only {len(created_questions) - (question_index - _)} available.")
                        break # 현재 사용자에게 더 이상 할당할 질문이 없으므로 다음 사용자로 넘어감

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
                        "title": db_question_set.title, # Include title here
                        "description": description
                    },
                    "generated_questions": [
                        {
                            "id": q.id,
                            "question": q.question,
                            "choices": json.loads(q.choices) if q.choices else [],
                            "answer": q.answer,
                            "max_score": q.max_score # Include max_score here
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

    def get_quiz_by_group(self, group_id: int) -> List[Dict[str, Any]]:
        """
        Get all quizzes for a specific group
        """
        try:
            question_sets = (
                self.db.query(QuestionSet)
                .filter(QuestionSet.group_id == group_id)
                .all()
            )

            result = []
            for qs in question_sets:
                # Get questions for this question set
                assignments = (
                    self.db.query(QuestionAssignment)
                    .filter(QuestionAssignment.question_set_id == qs.id)
                    .all()
                )

                questions = []
                for assignment in assignments:
                    question = (
                        self.db.query(Question)
                        .filter(Question.id == assignment.question_id)
                        .first()
                    )
                    if question:
                        questions.append({
                            "id": question.id,
                            "question": question.question,
                            "choices": json.loads(question.choices) if question.choices else [],
                            "answer": question.answer
                        })

                result.append({
                    "question_set_id": qs.id,
                    "group_id": qs.group_id,
                    "num_questions": qs.num_questions,
                    "description": qs.description,
                    "created_at": qs.created_at,
                    "questions": questions
                })

            return result

        except Exception as e:
            return {"error": f"Error retrieving quizzes: {str(e)}"}


def get_quiz_service(db: Session) -> QuizService:
    """
    Factory function to create QuizService instance
    """
    return QuizService(db)