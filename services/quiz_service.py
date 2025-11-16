"""
Quiz Service - Generate single-choice quizzes based on lecture content.
"""
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import Config
import json


class QuizService:
    """Service to generate single-choice quizzes from lecture content."""
    
    QUIZ_PROMPT_TEMPLATE = """You are an expert Romanian education assessment specialist who creates high-quality quiz questions based on educational content.

Given the following lecture content, create a single-choice quiz with exactly {num_questions} questions. 

IMPORTANT RULES:
1. Generate questions ONLY based on information explicitly stated in the provided content
2. Do NOT ask questions about information that is not in the content
3. Each question must have exactly 4 answer options (labeled a, b, c, d)
4. Only ONE option should be correct
5. Wrong options should be plausible but clearly incorrect based on the content
6. Questions should be in Romanian and appropriate for the target grade level
7. Distribute questions across the entire content to test comprehensive understanding
8. Vary the difficulty - include both basic recall and deeper understanding questions
9. Make sure each question is clear, unambiguous, and directly answerable from the content
10. Wrong answers should not be obviously wrong - they should require careful reading to distinguish

Lecture Content:
{content}

Your task: Generate exactly {num_questions} single-choice questions that comprehensively test understanding of this lecture content.

Output the quiz in the following JSON format:
{{
    "questions": [
        {{
            "id": "q1",
            "text": "Care este cea mai mică unitate vie a organismelor?",
            "options": [
                {{
                    "id": "a",
                    "text": "Celula"
                }},
                {{
                    "id": "b",
                    "text": "Țesutul"
                }},
                {{
                    "id": "c",
                    "text": "Organul"
                }},
                {{
                    "id": "d",
                    "text": "Sistemul"
                }}
            ],
            "correctAnswerId": "a"
        }}
    ]
}}

Generate the quiz now in Romanian:"""
    
    def __init__(self, model_name: str = None, temperature: float = 0.3):
        """
        Initialize the quiz service.
        
        Args:
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature for generation (0.3 for balanced creativity)
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
            template=self.QUIZ_PROMPT_TEMPLATE,
            input_variables=["content", "num_questions"]
        )
    
    def _clean_html(self, html_content: str) -> str:
        """
        Extract text content from HTML, removing tags but preserving structure.
        
        Args:
            html_content: HTML string with lecture content
            
        Returns:
            Cleaned text content
        """
        # Simple HTML tag removal (you could use BeautifulSoup for more robust parsing)
        import re
        
        # Remove HTML tags but keep the text
        text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove teacher notes (if any leaked through)
        text = re.sub(r'\[NOTĂ PROFESOR:.*?\]', '', text, flags=re.DOTALL)
        
        return text.strip()
    
    def generate_quiz(
        self,
        student_version: str,
        num_questions: int = 10
    ) -> Dict:
        """
        Generate a single-choice quiz based on lecture content.
        
        Args:
            student_version: HTML content from the student version of the lecture
            num_questions: Number of questions to generate (default: 10)
            
        Returns:
            Dictionary containing the quiz with questions, options, and correct answers
        """
        # Validate input
        if num_questions < 1:
            raise ValueError("Number of questions must be at least 1")
        
        if num_questions > 50:
            raise ValueError("Number of questions cannot exceed 50")
        
        if not student_version or len(student_version.strip()) < 100:
            raise ValueError("Student version content is too short to generate meaningful questions")
        
        # Clean HTML content
        cleaned_content = self._clean_html(student_version)
        
        print(f"Generating quiz with {num_questions} questions...")
        print(f"Content length: {len(cleaned_content)} characters")
        
        # Format the prompt
        formatted_prompt = self.prompt.format(
            content=cleaned_content,
            num_questions=num_questions
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
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
            
            quiz_data = json.loads(response_text)
            
            # Validate the structure
            if "questions" not in quiz_data:
                raise ValueError("Response missing 'questions' field")
            
            questions = quiz_data["questions"]
            
            if len(questions) != num_questions:
                print(f"Warning: Expected {num_questions} questions but got {len(questions)}")
            
            # Validate each question structure
            for i, q in enumerate(questions, 1):
                if "id" not in q or "text" not in q or "options" not in q or "correctAnswerId" not in q:
                    raise ValueError(f"Question {i} missing required fields")
                
                if len(q["options"]) != 4:
                    raise ValueError(f"Question {i} must have exactly 4 options")
                
                # Validate options
                for opt in q["options"]:
                    if "id" not in opt or "text" not in opt:
                        raise ValueError(f"Question {i} has invalid option structure")
                
                # Validate correct answer ID exists in options
                option_ids = [opt["id"] for opt in q["options"]]
                if q["correctAnswerId"] not in option_ids:
                    raise ValueError(f"Question {i}: correctAnswerId '{q['correctAnswerId']}' not found in options")
            
            print(f"✓ Generated quiz with {len(questions)} questions")
            
            return quiz_data
            
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON response: {e}")
            print(f"Raw response: {response_text[:500]}...")
            raise Exception(f"Failed to parse quiz from AI response: {str(e)}")
        except ValueError as e:
            print(f"Warning: Quiz validation failed: {e}")
            raise Exception(f"Generated quiz failed validation: {str(e)}")


if __name__ == "__main__":
    # Test the service
    print("Testing Quiz Service...\n")
    
    service = QuizService()
    
    # Test content
    student_version = """
    <h1>Celula - unitatea structurală și funcțională a vieții</h1>
    
    <h2>Introducere</h2>
    <p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule. 
    <strong>Celula</strong> este considerată unitatea structurală și funcțională a vieții deoarece toate procesele vitale au loc la nivel celular.</p>
    
    <h2>Structura celulei</h2>
    <p>Fiecare celulă este formată din mai multe componente importante:</p>
    <ul>
      <li><strong>Membrana celulară</strong> - învelișul exterior care protejează celula și controlează ce intră și iese din ea</li>
      <li><strong>Citoplasma</strong> - substanța gelatinoasă din interiorul celulei unde se desfășoară majoritatea proceselor vitale</li>
      <li><strong>Nucleul</strong> - centrul de comandă al celulei, care conține materialul genetic (ADN)</li>
    </ul>
    
    <h3>Celula animală vs. Celula vegetală</h3>
    <p>Există două tipuri principale de celule:</p>
    <ol>
      <li><strong>Celula animală</strong> - nu are perete celular, are forme variate</li>
      <li><strong>Celula vegetală</strong> - are perete celular rigid, conține cloroplaste pentru fotosinteză</li>
    </ol>
    """
    
    print(f"Generating quiz for biology lecture...")
    
    try:
        result = service.generate_quiz(
            student_version=student_version,
            num_questions=5
        )
        
        print("\nGenerated quiz:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
