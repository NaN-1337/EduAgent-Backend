"""
Homework Questions Service - Generate clarifying questions for homework preparation.
"""
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import Config


class HomeworkQuestionsService:
    """Service to generate clarifying questions for homework exercise creation."""
    
    PROMPT_TEMPLATE = """You are an expert Romanian education consultant who helps teachers create effective homework assignments.

Given the following parameters:
- Lesson Content Preview: {lesson_preview}
- Subject: {subject}
- Grade: {grade}
- Number of Exercises Requested: {num_exercises}

Your task is to generate 4-6 clarifying questions that will help gather important information for creating appropriate and effective homework exercises. These questions should help understand:
- The desired difficulty level and exercise types
- Student preparedness and prior knowledge
- Time expectations for homework completion
- Specific learning objectives to assess
- Whether hints or scaffolding should be provided
- Assessment focus areas

For each question, provide 2-5 response options that are commonly applicable. Include an "Altele" option where teachers might want to provide custom input.

Output the questions in the following JSON format:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Ce nivel de dificultate ar trebui să aibă exercițiile?",
            "type": "single-choice",
            "options": [
                "Ușor - consolidare concepte de bază",
                "Mediu - aplicare și înțelegere",
                "Dificil - analiză și sinteză",
                "Mixt - combinație de niveluri",
                "Altele"
            ]
        }},
        {{
            "id": 2,
            "question": "Ce tipuri de exerciții preferați?",
            "type": "multiple-choice",
            "options": [
                "Întrebări cu alegere multiplă",
                "Întrebări cu răspuns scurt",
                "Probleme de rezolvat",
                "Exerciții de aplicare practică",
                "Sarcini creative/proiecte",
                "Altele"
            ]
        }}
    ]
}}

Important rules:
1. All questions must be in Romanian
2. Questions should be specific to homework creation context
3. Use "single-choice" for questions with one answer
4. Use "multiple-choice" for questions where multiple selections make sense
5. Always include "Altele" as the last option for flexibility
6. Focus on pedagogically relevant aspects for homework
7. Consider the grade level when formulating questions
8. Questions should help tailor exercises to student needs

Generate the questions now:"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """
        Initialize the homework questions service.
        
        Args:
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature for generation
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
            input_variables=["lesson_preview", "subject", "grade", "num_exercises"]
        )
    
    def _extract_lesson_preview(self, lesson_content: str, max_length: int = 500) -> str:
        """Extract a preview of the lesson content for context."""
        # Strip HTML tags for cleaner preview
        import re
        clean_text = re.sub('<[^<]+?>', ' ', lesson_content)
        clean_text = ' '.join(clean_text.split())  # Normalize whitespace
        
        if len(clean_text) <= max_length:
            return clean_text
        
        return clean_text[:max_length] + "..."
    
    def generate_questions(
        self,
        lesson_content: str,
        num_exercises: int,
        subject: str,
        grade: int
    ) -> Dict:
        """
        Generate clarifying questions for homework preparation.
        
        Args:
            lesson_content: The lesson content (HTML or plain text)
            num_exercises: Number of exercises to be generated
            subject: Subject name (e.g., "Matematică", "Biologie")
            grade: Grade level (1-12)
            
        Returns:
            Dictionary containing generated questions with options
        """
        # Extract preview of lesson content
        lesson_preview = self._extract_lesson_preview(lesson_content)
        
        # Format the prompt
        formatted_prompt = self.prompt.format(
            lesson_preview=lesson_preview,
            subject=subject,
            grade=grade,
            num_exercises=num_exercises
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
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
                        "question": "A apărut o eroare la generarea întrebărilor. Răspunde DA pentru a continua cu setările implicite.",
                        "type": "yes-no",
                        "options": ["Da", "Nu"]
                    }
                ],
                "error": str(e)
            }


if __name__ == "__main__":
    # Test the service
    print("Testing Homework Questions Service...\n")
    
    service = HomeworkQuestionsService()
    
    # Test case
    lesson_content = """
    <h1>Celula - unitatea structurală și funcțională a vieții</h1>
    <h2>Introducere</h2>
    <p>Celula este cea mai mică unitate structurală și funcțională a vieții.
    Toate organismele vii sunt formate din una sau mai multe celule...</p>
    """
    
    num_exercises = 5
    subject = "Biologie"
    grade = 6
    
    print(f"Generating questions for homework with:")
    print(f"  Subject: {subject}")
    print(f"  Grade: {grade}")
    print(f"  Number of exercises: {num_exercises}\n")
    
    result = service.generate_questions(lesson_content, num_exercises, subject, grade)
    
    print("Generated questions:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))
