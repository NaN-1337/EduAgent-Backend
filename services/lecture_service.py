"""
Lecture Service - Generate student and teacher versions of lectures using RAG.
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from vector_store import VectorStoreManager
from config import Config


class LectureService:
    """Service to generate student and teacher lecture materials using RAG."""
    
    # Prompt template for generating student version
    STUDENT_PROMPT_TEMPLATE = """You are an expert Romanian education content creator specializing in creating student-friendly learning materials.

Context from curriculum documents:
{context}

Lecture Parameters:
- Title: {title}
- Subject: {subject}
- Grade: {grade}

Teacher's Clarifying Information:
{clarifications}

Your task is to generate a comprehensive lecture text designed specifically for students at grade {grade}. The content should:
1. Be written in clear, age-appropriate Romanian language
2. Cover all essential concepts related to the topic
3. Use simple examples and explanations suitable for the grade level
4. Include key terminology with definitions
5. Be structured logically with clear sections
6. Be comprehensive enough that students can learn the topic thoroughly by reading it

Format the output in HTML with basic styling:
- Use <h1> for the main title
- Use <h2> for major sections
- Use <h3> for subsections
- Use <p> for paragraphs
- Use <strong> for important terms
- Use <em> for emphasis
- Use <ul> and <li> for lists
- Use <ol> for numbered lists when appropriate

The content should be complete and self-contained, allowing students to understand the topic without additional resources.

Generate the student lecture now:"""

    # Prompt template for generating teacher version
    TEACHER_PROMPT_TEMPLATE = """You are an expert Romanian education consultant helping teachers deliver effective lessons.

Context from curriculum documents:
{context}

Lecture Parameters:
- Title: {title}
- Subject: {subject}
- Grade: {grade}

Teacher's Clarifying Information:
{clarifications}

Student Version Content:
{student_content}

Your task is to enhance the student version with additional teaching guidance and advanced information for the teacher. This enhanced version should:
1. Include all content from the student version
2. Add [NOTĂ PROFESOR: ...] annotations with:
   - Advanced explanations or background information
   - Common misconceptions students might have
   - Teaching tips and presentation suggestions
   - Discussion questions to engage students
   - Additional examples or analogies
   - Cross-curriculum connections
   - Assessment suggestions
3. Highlight key concepts the teacher should emphasize
4. Suggest pacing and time allocation for different sections
5. Include deeper scientific/subject knowledge that teachers can use but might not share directly with students

Format the output in HTML with basic styling (same tags as student version), but add:
- Use <div class="teacher-note"> for teacher-specific annotations
- Use <span class="emphasis"> for key teaching points
- Integrate teacher notes naturally within the content flow

Generate the enhanced teacher lecture now:"""
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        model_name: str = None,
        temperature: float = 0.2
    ):
        """
        Initialize the lecture service.
        
        Args:
            vector_store_manager: VectorStoreManager instance. If None, creates new one.
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature for generation
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
        
        self.student_prompt = PromptTemplate(
            template=self.STUDENT_PROMPT_TEMPLATE,
            input_variables=["context", "title", "subject", "grade", "clarifications"]
        )
        
        self.teacher_prompt = PromptTemplate(
            template=self.TEACHER_PROMPT_TEMPLATE,
            input_variables=["context", "title", "subject", "grade", "clarifications", "student_content"]
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
    
    def generate_lecture(
        self,
        title: str,
        subject: str,
        grade: int,
        questions: List[Dict],
        answers: Dict,
        top_k: int = None
    ) -> Dict[str, str]:
        """
        Generate both student and teacher versions of a lecture.
        
        Args:
            title: Lecture title/topic
            subject: Subject name (e.g., "Matematică", "Biologie")
            grade: Grade level (1-12)
            questions: List of clarifying questions (from first endpoint)
            answers: Dictionary mapping question IDs to answers
            top_k: Number of documents to retrieve. If None, uses Config.TOP_K_RESULTS
            
        Returns:
            Dictionary with 'student_version' and 'teacher_version' keys containing HTML content
        """
        # Retrieve relevant documents with metadata filtering
        query = f"{title} {subject}"
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
        
        # Generate student version
        print("Generating student version...")
        student_prompt = self.student_prompt.format(
            context=context,
            title=title,
            subject=subject,
            grade=grade,
            clarifications=clarifications
        )
        
        student_response = self.llm.invoke(student_prompt)
        student_content = student_response.content if hasattr(student_response, 'content') else str(student_response)
        
        # Clean up markdown code blocks if present
        student_content = self._clean_html_response(student_content)
        
        # Generate teacher version
        print("Generating teacher version...")
        teacher_prompt = self.teacher_prompt.format(
            context=context,
            title=title,
            subject=subject,
            grade=grade,
            clarifications=clarifications,
            student_content=student_content
        )
        
        teacher_response = self.llm.invoke(teacher_prompt)
        teacher_content = teacher_response.content if hasattr(teacher_response, 'content') else str(teacher_response)
        
        # Clean up markdown code blocks if present
        teacher_content = self._clean_html_response(teacher_content)
        
        return {
            "student_version": student_content,
            "teacher_version": teacher_content
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
    print("Testing Lecture Service...\n")
    
    service = LectureService()
    
    # Test case
    title = "Celula - unitatea structurală și funcțională a vieții"
    subject = "biologie"
    grade = 6
    
    questions = [
        {"id": 1, "question": "Care este scopul principal al lecției?"},
        {"id": 2, "question": "Cât timp este alocat pentru această lecție?"}
    ]
    
    answers = {
        "1": "Introducerea conceptelor noi",
        "2": "50 minute (o oră)"
    }
    
    print(f"Generating lecture for:")
    print(f"  Title: {title}")
    print(f"  Subject: {subject}")
    print(f"  Grade: {grade}\n")
    
    result = service.generate_lecture(title, subject, grade, questions, answers)
    
    print("\n" + "="*60)
    print("Student Version Preview (first 500 chars):")
    print("="*60)
    print(result["student_version"][:500])
    
    print("\n" + "="*60)
    print("Teacher Version Preview (first 500 chars):")
    print("="*60)
    print(result["teacher_version"][:500])