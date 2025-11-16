"""
Questions Service - Generate clarifying questions for lecture preparation.
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import Config


class QuestionsService:
    """Service to generate clarifying questions based on lecture parameters."""
    
    PROMPT_TEMPLATE = """You are an expert Romanian education consultant who helps teachers prepare high-quality lessons.

Given the following lecture parameters:
- Title/Topic: {title}
- Subject: {subject}
- Grade: {grade}

Your task is to generate 5-8 clarifying questions that will help gather important information for creating a comprehensive and effective lesson. These questions should be based on pedagogical best practices and help understand:
- The specific focus areas within the topic
- The desired learning outcomes
- The students' prior knowledge level
- Teaching methodology preferences
- Time constraints
- Available resources
- Assessment preferences

For each question, provide 2-5 response options that are commonly applicable. Include an "Other" option where teachers might want to provide custom input.

Output the questions in the following JSON format:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Care este scopul principal al lecției?",
            "type": "single-choice",
            "options": [
                "Introducerea conceptelor noi",
                "Aprofundarea cunoștințelor existente",
                "Pregătirea pentru evaluare",
                "Altele"
            ]
        }},
        {{
            "id": 2,
            "question": "Cât timp este alocat pentru această lecție?",
            "type": "single-choice",
            "options": [
                "30 minute",
                "45 minute",
                "50 minute (o oră)",
                "100 minute (două ore)",
                "Altele"
            ]
        }}
    ]
}}

Important rules:
1. All questions must be in Romanian
2. Questions should be specific and actionable
3. Use "single-choice" for questions with predefined options
4. Use "yes-no" for binary questions
5. Always include "Altele" as the last option for flexibility
6. Focus on pedagogically relevant aspects
7. Consider the grade level and subject when formulating questions

Generate the questions now:"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """
        Initialize the questions service.
        
        Args:
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature for generation (slightly higher for creativity)
        """
        self.model_name = model_name or Config.OPENAI_MODEL
        self.temperature = temperature
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        self.prompt = PromptTemplate(
            template=self.PROMPT_TEMPLATE,
            input_variables=["title", "subject", "grade"]
        )
    
    def generate_questions(self, title: str, subject: str, grade: int) -> Dict:
        """
        Generate clarifying questions for lecture preparation.
        
        Args:
            title: Lecture title/topic
            subject: Subject name (e.g., "Matematică", "Biologie")
            grade: Grade level (1-12)
            
        Returns:
            Dictionary containing generated questions with options
        """
        # Format the prompt
        formatted_prompt = self.prompt.format(
            title=title,
            subject=subject,
            grade=grade
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
        # The LLM should return valid JSON, but we'll handle it gracefully
        import json
        
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            questions_data = json.loads(response_text)
            return questions_data
        except json.JSONDecodeError as e:
            # Fallback: return error structure
            print(f"Warning: Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {
                "questions": [
                    {
                        "id": 1,
                        "question": "A apărut o eroare la generarea întrebărilor. Răspunde DA pentru a continua cu informațiile de bază.",
                        "type": "yes-no",
                        "options": ["Da", "Nu"]
                    }
                ],
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the service
    print("Testing Questions Service...\n")
    
    service = QuestionsService()
    
    # Test case
    title = "Celula - unitatea structurală și funcțională a vieții"
    subject = "Biologie"
    grade = 6
    
    print(f"Generating questions for:")
    print(f"  Title: {title}")
    print(f"  Subject: {subject}")
    print(f"  Grade: {grade}\n")
    
    result = service.generate_questions(title, subject, grade)
    
    print("Generated questions:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))