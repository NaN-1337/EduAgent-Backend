"""
Homework Service - Generate homework exercises from lesson content using RAG.
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from vector_store import VectorStoreManager
from config import Config


class HomeworkService:
    """Service to generate homework exercises based on lesson content using RAG."""
    
    # Prompt template for generating homework exercises
    HOMEWORK_PROMPT_TEMPLATE = """You are an expert Romanian education content creator specializing in creating effective homework exercises.

Context from curriculum documents:
{context}

Lesson Content:
{lesson_content}

Exercise Parameters:
- Subject: {subject}
- Grade: {grade}
- Number of Exercises: {num_exercises}

Teacher's Clarifying Information:
{clarifications}

Your task is to generate {num_exercises} homework exercises based on the provided lesson content. The exercises should:
1. Be written in clear, age-appropriate Romanian language
2. Directly relate to concepts covered in the lesson
3. Progress from easier to more challenging (scaffolded difficulty)
4. Include a variety of exercise types:
   - Multiple choice questions
   - Short answer questions
   - Problem-solving exercises
   - Application/analysis questions
   - Creative tasks (where appropriate)
5. Be appropriate for grade {grade} students
6. Align with Romanian curriculum standards
7. Include clear instructions for each exercise
8. Provide point values for each exercise

Format the output in HTML with basic styling:
- Use <h1> for the main title "Temă pentru acasă - [Subject]"
- Use <h2> for section headers
- Use <div class="exercise"> for each exercise container
- Use <div class="exercise-header"> for exercise number and points
- Use <div class="exercise-content"> for the exercise text
- Use <p> for instructions and questions
- Use <strong> for important terms
- Use <ul> and <li> for multiple choice options
- Use <div class="hint"> for optional hints (if requested)

Each exercise should have this structure:
<div class="exercise">
  <div class="exercise-header">
    <span class="exercise-number">Exercițiul 1</span>
    <span class="points">(10 puncte)</span>
  </div>
  <div class="exercise-content">
    <p>Exercise text here...</p>
  </div>
</div>

Generate the homework exercises now:"""
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        model_name: str = None,
        temperature: float = 0.3
    ):
        """
        Initialize the homework service.
        
        Args:
            vector_store_manager: VectorStoreManager instance. If None, creates new one.
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature for generation (slightly higher for variety)
        """
        self.vs_manager = vector_store_manager or VectorStoreManager()
        
        # Load vector store
        try:
            self.vs_manager.load_vector_store()
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            raise
        
        self.model_name = model_name or Config.OPENAI_MODEL
        self.temperature = temperature
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        self.prompt = PromptTemplate(
            template=self.HOMEWORK_PROMPT_TEMPLATE,
            input_variables=["context", "lesson_content", "subject", "grade", "num_exercises", "clarifications"]
        )
    
    def _format_docs(self, docs) -> str:
        """Format retrieved documents into a single context string."""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            formatted.append(
                f"[Document {i} - Source: {source}, Page: {page}]\n{doc.page_content}"
            )
        return "\n\n".join(formatted)
    
    def _format_clarifications(self, questions: List[Dict], answers: Dict) -> str:
        """Format questions and answers into a readable string."""
        lines = []
        for q in questions:
            q_id = q.get('id')
            question = q.get('question')
            answer = answers.get(str(q_id), 'No answer provided')
            lines.append(f"- {question}\n  Răspuns: {answer}")
        return "\n".join(lines)
    
    def generate_homework(
        self,
        lesson_content: str,
        num_exercises: int,
        subject: str,
        grade: int,
        questions: List[Dict],
        answers: Dict,
        top_k: int = None
    ) -> Dict[str, str]:
        """
        Generate homework exercises based on lesson content.
        
        Args:
            lesson_content: The lesson content (HTML or plain text)
            num_exercises: Number of exercises to generate
            subject: Subject name (e.g., "Matematică", "Biologie")
            grade: Grade level (1-12)
            questions: List of clarifying questions (from homework questions endpoint)
            answers: Dictionary mapping question IDs to answers
            top_k: Number of documents to retrieve. If None, uses Config.TOP_K_RESULTS
            
        Returns:
            Dictionary with 'homework' key containing HTML content
        """
        # Retrieve relevant documents with metadata filtering
        # Extract key concepts from lesson for better search
        query = f"{subject} exerciții temă"
        docs = self.vs_manager.similarity_search(
            query=query,
            k=top_k or Config.TOP_K_RESULTS,
            filter={
                "$and": [
                    {"subject": subject.lower()},
                    {"grade": grade}
                ]
            }
        )
        
        context = self._format_docs(docs)
        clarifications = self._format_clarifications(questions, answers)
        
        # Generate homework exercises
        print(f"Generating {num_exercises} homework exercises...")
        homework_prompt = self.prompt.format(
            context=context,
            lesson_content=lesson_content,
            subject=subject,
            grade=grade,
            num_exercises=num_exercises,
            clarifications=clarifications
        )
        
        homework_response = self.llm.invoke(homework_prompt)
        homework_content = homework_response.content if hasattr(homework_response, 'content') else str(homework_response)
        
        # Clean up markdown code blocks if present
        homework_content = self._clean_html_response(homework_content)
        
        return {
            "homework": homework_content
        }
    
    def _clean_html_response(self, content: str) -> str:
        """Remove markdown code block markers if present."""
        if "```html" in content:
            start = content.find("```html") + 7
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        return content


if __name__ == "__main__":
    # Test the service
    print("Testing Homework Service...\n")
    
    service = HomeworkService()
    
    # Test case with sample lesson content
    lesson_content = """
    <h1>Celula - unitatea structurală și funcțională a vieții</h1>
    <h2>Introducere</h2>
    <p>Celula este cea mai mică unitate structurală și funcțională a vieții...</p>
    """
    
    subject = "biologie"
    grade = 6
    num_exercises = 5
    
    questions = [
        {"id": 1, "question": "Ce tip de exerciții preferați?"},
        {"id": 2, "question": "Care este nivelul de dificultate dorit?"}
    ]
    
    answers = {
        "1": "Combinație de tipuri",
        "2": "Mediu"
    }
    
    print(f"Generating homework for:")
    print(f"  Subject: {subject}")
    print(f"  Grade: {grade}")
    print(f"  Number of exercises: {num_exercises}\n")
    
    result = service.generate_homework(
        lesson_content=lesson_content,
        num_exercises=num_exercises,
        subject=subject,
        grade=grade,
        questions=questions,
        answers=answers
    )
    
    print("\n" + "="*60)
    print("Homework Preview (first 800 chars):")
    print("="*60)
    print(result["homework"][:800])
