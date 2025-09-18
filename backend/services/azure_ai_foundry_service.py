import httpx
import json
import asyncio
from typing import Dict, Any, List, Optional
from models.group import Group
from config import settings


class BaseAIFoundryService:
    """Base service for Microsoft AI Foundry Agent operations following ai-foundry-agent.md"""

    def __init__(self):
        self.client = httpx.AsyncClient()

        # Fixed values from ai-foundry-agent.md
        self.tenant_id = "3efeebc6-c535-4752-bd40-97f1078c7209"
        self.client_id = "dbee27d5-529b-499c-9f32-e0ebe8f525be"
        self.client_secret = "aGV8Q~U0g_fr8gFAjraiIvZiNRjMzbLc_neUCcTl"
        self.base_url = "https://yesong.services.ai.azure.com/api/projects/yesong-project"
        self.scope = "https://ai.azure.com/.default"

        self.access_token = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def get_access_token(self) -> str:
        """Step 1: Get OAuth access token following ai-foundry-agent.md"""
        try:
            token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }

            body = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope
            }

            print(f"Getting access token from: {token_url}")

            response = await self.client.post(
                token_url,
                headers=headers,
                data=body,
                timeout=30.0
            )

            print(f"Token response status: {response.status_code}")

            if response.status_code != 200:
                print(f"Token request failed: {response.text}")
                return None

            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data.get("access_token")
            print(f"Access token acquired successfully")

            return self.access_token

        except Exception as e:
            print(f"Error getting access token: {str(e)}")
            return None

    async def create_thread(self) -> Optional[str]:
        """Step 2: Create thread following ai-foundry-agent.md"""
        try:
            if not self.access_token:
                await self.get_access_token()

            if not self.access_token:
                return None

            thread_url = f"{self.base_url}/threads?api-version=v1"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }

            print(f"Creating thread at: {thread_url}")

            response = await self.client.post(
                thread_url,
                headers=headers,
                json={},
                timeout=30.0
            )

            print(f"Thread creation response status: {response.status_code}")

            if response.status_code != 200:
                print(f"Thread creation failed: {response.text}")
                return None

            response.raise_for_status()
            thread_data = response.json()

            thread_id = thread_data.get("id")
            print(f"Thread created: {thread_id}")

            return thread_id

        except Exception as e:
            print(f"Error creating thread: {str(e)}")
            return None

    async def set_message(self, thread_id: str, prompt: str) -> bool:
        """Step 3: Set message following ai-foundry-agent.md"""
        try:
            message_url = f"{self.base_url}/threads/{thread_id}/messages?api-version=v1"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }

            body = {
                "role": "user",
                "content": prompt
            }

            print(f"Setting message at: {message_url}")

            response = await self.client.post(
                message_url,
                headers=headers,
                json=body,
                timeout=30.0
            )

            print(f"Message setting response status: {response.status_code}")

            if response.status_code != 200:
                print(f"Message setting failed: {response.text}")
                return False

            response.raise_for_status()
            print("Message set successfully")

            return True

        except Exception as e:
            print(f"Error setting message: {str(e)}")
            return False

    async def run_agent(self, thread_id: str, agent_id: str) -> bool:
        """Step 4: Run agent following ai-foundry-agent.md"""
        try:
            run_url = f"{self.base_url}/threads/{thread_id}/runs?api-version=v1"

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.access_token}"
            }

            body = {
                "assistant_id": agent_id,
                "stream": True
            }

            print(f"Running agent at: {run_url}")
            print(f"Using agent ID: {agent_id}")

            response = await self.client.post(
                run_url,
                headers=headers,
                json=body,
                timeout=60.0
            )

            print(f"Agent run response status: {response.status_code}")

            # According to ai-foundry-agent.md, ignore response if not failure
            if response.status_code >= 400:
                print(f"Agent run failed: {response.text}")
                return False

            print("Agent run initiated successfully")
            return True

        except Exception as e:
            print(f"Error running agent: {str(e)}")
            return False

    async def get_result(self, thread_id: str, max_attempts: int = 30) -> Optional[str]:
        """Step 5: Get result following ai-foundry-agent.md"""
        try:
            result_url = f"{self.base_url}/threads/{thread_id}/messages?api-version=v1"

            headers = {
                "Authorization": f"Bearer {self.access_token}"
            }

            # Wait for agent to complete processing
            for attempt in range(max_attempts):
                print(f"Getting result (attempt {attempt + 1}): {result_url}")

                response = await self.client.get(
                    result_url,
                    headers=headers,
                    timeout=30.0
                )

                print(f"Result response status: {response.status_code}")

                if response.status_code != 200:
                    print(f"Result request failed: {response.text}")
                    await asyncio.sleep(2)
                    continue

                result_data = response.json()

                # Find assistant's response (role=assistant)
                data_list = result_data.get("data", [])

                for message in data_list:
                    if message.get("role") == "assistant":
                        content_list = message.get("content", [])

                        for content_item in content_list:
                            if content_item.get("type") == "text":
                                text_obj = content_item.get("text", {})
                                value = text_obj.get("value", "")

                                if value.strip():
                                    print(f"Assistant response received: {value[:200]}...")
                                    return value

                # If no assistant response yet, wait and retry
                print(f"No assistant response yet, waiting...")
                await asyncio.sleep(2)

            print("Timeout waiting for agent response")
            return None

        except Exception as e:
            print(f"Error getting result: {str(e)}")
            return None

    async def call_agent(self, agent_id: str, prompt: str) -> Optional[str]:
        """Complete 5-step agent call following ai-foundry-agent.md"""
        try:
            # Step 1: Get token
            if not await self.get_access_token():
                return None

            # Step 2: Create thread
            thread_id = await self.create_thread()
            if not thread_id:
                return None

            # Step 3: Set message
            if not await self.set_message(thread_id, prompt):
                return None

            # Step 4: Run agent
            if not await self.run_agent(thread_id, agent_id):
                return None

            # Step 5: Get result
            return await self.get_result(thread_id)

        except Exception as e:
            print(f"Error in agent call: {str(e)}")
            return None


class QuizGenerationService(BaseAIFoundryService):
    """Quiz generation service using AI Foundry Agent"""

    def __init__(self):
        super().__init__()

    def build_quiz_prompt(self, group: Group, num_questions: int, language: str, difficulty: str, description: str, user_count: int = 1) -> str:
        """Build prompt for quiz generation based on group information"""

        # Check if description contains specific question type requirements
        has_specific_type_request = any(keyword in description.lower() for keyword in [
            '객관식', '주관식', 'multiple choice', 'short answer', 'essay',
            'trắc nghiệm', 'tự luận', '多肢選択', '短答', 'choice', 'answer'
        ])

        # The prompt is always in Korean, but it requests the quiz in the specified language.
        prompt = f"""퀴즈를 생성해주세요.

**요청 언어:** {language} (이 언어로 문제를 출제해주세요.)

**교육 대상:** {group.name}
**교육 목적:** {group.memo or '일반 교육'}
**총 문제 수:** {num_questions} * {user_count} 개 (그룹 내 {user_count}명의 사용자가 각각 다른 문제를 받을 예정)
**난이도:** {difficulty}
**추가 요구사항:** {description}

**중요 지시사항:**
1.  각 사용자가 서로 다른 문제를 받을 수 있도록 다양하고 독창적인 {num_questions} * {user_count}개의 문제를 생성해주세요.
2.  같은 주제나 개념이라도 다른 관점이나 접근 방식으로 문제를 출제해주세요.
3.  각 문제의 배점('max_score')은 1인당 총점 100점을 준수하여 문항별 난이도를 고려해 알아서 설정해 주세요.

**응답 형식 (JSON):**
응답은 반드시 다음 JSON 형식을 따라야 합니다. 다른 설명 없이 JSON 객체만 반환해주세요.
{{
  "questions": [
    {{
      "question": "Content of the question in the requested language",
      "type": "M",
      "choices": ["Choice 1 text", "Choice 2 text", "Choice 3 text", "Choice 4 text"],
      "answer": "The full text of the correct answer from the choices list",
      "max_score": "Score is distributed based on the difficulty of each question (the total score per person must be 100 points)"
    }},
    {{
      "question": "Content of the short answer question in the requested language",
      "type": "S",
      "choices": null,
      "answer": "The expected answer for the short answer question",
      "max_score": "Score is distributed based on the difficulty of each question (the total score per person must be 100 points)"
    }}
  ]
}}

**필드 설명:**
- `type`: "M"(객관식) 또는 "S"(주관식) 중 하나여야 합니다.
- `choices`: 객관식의 경우, 반드시 4개의 **문자열**을 포함하는 리스트여야 합니다. Key/Value 형태가 아닌, 선택지 텍스트의 리스트입니다.
- `answer`: 객관식의 경우, 반드시 `choices` 리스트에 있는 **정답의 전체 텍스트**를 그대로 기입해야 합니다. 'A'나 '1'과 같은 번호나 문자가 아닌, 실제 정답 내용을 기입해주세요.

{"다양성을 위해 객관식과 주관식 문제를 모두 포함해주세요." if not has_specific_type_request else "추가 요구사항에서 언급된 구체적인 문제 유형 요구사항을 따라주세요."} 각 문제는 교육 대상과 목적에 맞게 구성해주세요."""

        return prompt

    async def generate_quiz(self, group: Group, num_questions: int, language: str, difficulty: str, description: str, user_count: int = 1) -> Dict[str, Any]:
        """Generate quiz using AI Foundry Agent following ai-foundry-agent.md"""
        try:
            # Get agent ID from settings
            agent_id = settings.ai_foundry_agent_id
            if not agent_id:
                return {"error": "AI Foundry agent ID not configured"}

            print(f"Using AI Foundry Agent API")
            print(f"Agent ID: {agent_id}")

            # Build prompt
            prompt = self.build_quiz_prompt(group, num_questions, language, difficulty, description, user_count)
            print(f"Sending prompt to AI Foundry agent: {prompt}")

            # Call agent following 5-step pattern
            ai_response = await self.call_agent(agent_id, prompt)

            if not ai_response:
                return {"error": "Failed to get response from AI Foundry agent"}

            print(f"AI response received: {ai_response[:200]}...")

            # Extract quiz data from AI response
            quiz_data = self.extract_quiz_from_response(ai_response)

            if "error" in quiz_data:
                print(f"Quiz extraction error: {quiz_data['error']}")
            else:
                print(f"Successfully extracted {len(quiz_data.get('questions', []))} questions")

            return quiz_data

        except Exception as e:
            print(f"Error generating quiz: {str(e)}")
            return {"error": f"Error generating quiz: {str(e)}"}

    def extract_quiz_from_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract quiz JSON from AI response text"""
        try:
            # Remove markdown code blocks if present
            if "```json" in ai_response:
                start = ai_response.find("```json") + 7
                end = ai_response.find("```", start)
                if end != -1:
                    ai_response = ai_response[start:end].strip()
            elif "```" in ai_response:
                start = ai_response.find("```") + 3
                end = ai_response.find("```", start)
                if end != -1:
                    ai_response = ai_response[start:end].strip()

            # Try to find JSON object in the text
            json_start = ai_response.find("{")
            json_end = ai_response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_text = ai_response[json_start:json_end]
                quiz_data = json.loads(json_text)
                return quiz_data
            else:
                # Try parsing the entire text
                quiz_data = json.loads(ai_response)
                return quiz_data

        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON response: {str(e)}", "raw_response": ai_response}
        except Exception as e:
            return {"error": f"Error parsing response: {str(e)}", "raw_response": ai_response}

    def validate_quiz_response(self, quiz_data: Dict[str, Any]) -> bool:
        """Validate the quiz response format"""
        if "questions" not in quiz_data:
            print("Validation failed: 'questions' key missing from quiz_data")
            return False

        questions = quiz_data["questions"]
        if not isinstance(questions, list):
            print("Validation failed: 'questions' is not a list")
            return False

        for i, question in enumerate(questions):
            print(f"Validating question {i+1}...")
            required_fields = ["question", "type", "choices", "answer"]
            if not all(field in question for field in required_fields):
                print(f"Validation failed for question {i+1}: Missing one or more required fields. Found: {list(question.keys())}")
                return False

            # For multiple choice questions, validate choices
            if question.get("type") == "M":
                if not isinstance(question.get("choices"), list):
                    print(f"Validation failed for question {i+1}: 'choices' is not a list for a multiple choice question.")
                    return False
                if len(question["choices"]) != 4:
                    print(f"Validation failed for question {i+1}: Expected 4 choices, but got {len(question['choices'])}")
                    return False
                if question["answer"] not in question["choices"]:
                    print(f"Validation failed for question {i+1}: Answer '{question['answer']}' not found in choices {question['choices']}")
                    return False
            
            # For short answer questions, choices can be null/empty
            elif question.get("type") == "S":
                # No specific validation for short answer choices needed for now
                pass
            
            else:
                print(f"Validation failed for question {i+1}: Invalid question type '{question.get('type')}'")
                return False

        print("All questions validated successfully.")
        return True


# Legacy class name for backward compatibility
class AzureAIFoundryService(QuizGenerationService):
    """Legacy wrapper for backward compatibility"""
    pass


# Factory function for dependency injection
async def get_azure_ai_foundry_service() -> QuizGenerationService:
    """Factory function to create QuizGenerationService instance"""
    return QuizGenerationService()