"""
Chatbot Service - Educational assistant with role-based adaptation and web search.
"""
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from config import Config


class ChatbotService:
    """
    Educational chatbot that adapts its tone and communication style based on user role.
    Supports two user roles: student (with grade level) and individual (adult learner).
    """
    
    # System prompts for different user roles
    STUDENT_SYSTEM_PROMPT = """You are a friendly and helpful educational assistant for Romanian students. You are helping a student in grade {grade} learn about {subject}.

Your communication style for grade {grade}:
{tone_guidance}

Lesson Content Context:
{lesson_content}

Guidelines:
1. Always respond in Romanian
2. Use age-appropriate language and examples
3. Be encouraging and supportive
4. Break down complex concepts into simpler parts
5. Use analogies and real-world examples relevant to their age
6. If you don't know something, be honest and suggest where they can find more information
7. You have access to web search - use it when needed for current information or additional examples
8. Focus on helping them understand, not just giving answers
9. Ask clarifying questions if their query is unclear
10. Relate concepts back to the lesson content when relevant

Remember: You're helping them learn and understand, not just complete homework for them."""

    INDIVIDUAL_SYSTEM_PROMPT = """You are a professional educational assistant for adult learners in Romania. You are helping an independent learner who is studying educational materials.

Lesson Content Context:
{lesson_content}

Guidelines:
1. Always respond in Romanian
2. Use clear, professional language suitable for adults
3. Provide comprehensive, detailed explanations
4. Include relevant context and background information
5. Reference credible sources when appropriate
6. You have access to web search - use it for current information and verification
7. Be direct and efficient in your responses
8. Assume they can handle complex concepts but may need context
9. If they're preparing for exams, provide structured study guidance
10. Relate concepts back to the lesson content when relevant

Remember: You're supporting their self-directed learning journey with respect for their adult learning needs."""

    # Tone guidance for different grade levels
    GRADE_TONE_GUIDANCE = {
        "1-4": """For grades 1-4 (ages 7-10):
- Use very simple, playful language
- Include fun comparisons and examples from their daily life
- Use emojis occasionally to keep it engaging
- Keep sentences short and clear
- Encourage them frequently with positive reinforcement
- Use storytelling when explaining concepts""",
        
        "5-8": """For grades 5-8 (ages 11-14):
- Use friendly, conversational language
- Balance playfulness with learning
- Use examples from their interests (games, sports, social media)
- Introduce some technical terms but explain them clearly
- Encourage curiosity and questions
- Be supportive but not overly childish""",
        
        "9-12": """For grades 9-12 (ages 15-18):
- Use mature, respectful language
- Be more direct and academic in tone
- Use real-world applications and career connections
- Assume they can handle complexity
- Encourage critical thinking
- Prepare them for university-level learning
- Be supportive but treat them as young adults"""
    }
    
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        """
        Initialize the chatbot service.
        
        Args:
            model_name: OpenAI model name (default: gpt-4o for web search capability)
            temperature: Model temperature for more conversational responses
        """
        self.model_name = model_name
        self.temperature = temperature
        
        # Initialize GPT-4o for web search capability
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
    
    def _get_tone_guidance(self, grade: int) -> str:
        """Get tone guidance based on grade level."""
        if 1 <= grade <= 4:
            return self.GRADE_TONE_GUIDANCE["1-4"]
        elif 5 <= grade <= 8:
            return self.GRADE_TONE_GUIDANCE["5-8"]
        elif 9 <= grade <= 12:
            return self.GRADE_TONE_GUIDANCE["9-12"]
        else:
            return self.GRADE_TONE_GUIDANCE["5-8"]  # Default to middle school
    
    def _clean_lesson_content(self, lesson_content: str, max_length: int = 3000) -> str:
        """Clean and truncate lesson content for context."""
        import re
        
        # Remove HTML tags
        clean_text = re.sub('<[^<]+?>', ' ', lesson_content)
        
        # Normalize whitespace
        clean_text = ' '.join(clean_text.split())
        
        # Truncate if too long
        if len(clean_text) > max_length:
            clean_text = clean_text[:max_length] + "..."
        
        # Escape curly braces for LangChain template (double them)
        # This prevents LangChain from treating CSS properties or other {content} as variables
        clean_text = clean_text.replace('{', '{{').replace('}', '}}')
        
        return clean_text
    
    def chat(
        self,
        user_prompt: str,
        lesson_content: str,
        subject: str,
        user_role: str,
        grade: Optional[int] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate a chatbot response based on user role and context.
        
        Args:
            user_prompt: The user's question or message
            lesson_content: The lesson content (HTML from /api/generate-lecture)
            subject: Subject name (e.g., "Biologie", "Matematică")
            user_role: Either "student" or "individual"
            grade: Grade level (1-12, required if user_role is "student")
            conversation_history: List of previous messages [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Dictionary with:
                - response: The chatbot's response text
                - conversation_history: Updated conversation history
        """
        # Validate user_role
        if user_role not in ["student", "individual"]:
            raise ValueError("user_role must be either 'student' or 'individual'")
        
        # Validate grade for students
        if user_role == "student":
            if grade is None:
                raise ValueError("grade is required when user_role is 'student'")
            if not (1 <= grade <= 12):
                raise ValueError("grade must be between 1 and 12")
        
        # Initialize conversation history if not provided
        if conversation_history is None:
            conversation_history = []
        
        # Clean and prepare lesson content
        clean_content = self._clean_lesson_content(lesson_content)
        
        # Build system prompt based on user role
        if user_role == "student":
            tone_guidance = self._get_tone_guidance(grade)
            system_prompt = self.STUDENT_SYSTEM_PROMPT.format(
                grade=grade,
                subject=subject,
                tone_guidance=tone_guidance,
                lesson_content=clean_content
            )
        else:  # individual
            system_prompt = self.INDIVIDUAL_SYSTEM_PROMPT.format(
                lesson_content=clean_content
            )
        
        # Build message history for LangChain
        messages = [("system", system_prompt)]
        
        # Add conversation history
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "user":
                messages.append(("human", content))
            elif role == "assistant":
                messages.append(("ai", content))
        
        # Add current user prompt
        messages.append(("human", user_prompt))
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(messages)
        
        # Generate response
        chain = prompt | self.llm
        response = chain.invoke({})
        
        # Extract response text
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Update conversation history
        updated_history = conversation_history + [
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": response_text}
        ]
        
        return {
            "response": response_text,
            "conversation_history": updated_history
        }
