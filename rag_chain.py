"""
RAG Chain module - Implements the complete Retrieval-Augmented Generation pipeline.
"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from vector_store import VectorStoreManager
from memory import ConversationMemory
from config import Config


class RAGChain:
    """Retrieval-Augmented Generation chain for question answering."""
    
    # Prompt template for Romanian educational materials generation
    PROMPT_TEMPLATE = """You are an expert AI assistant trained to generate educational materials for Romanian teachers, using curriculum context provided in the following context, which comes from official Romanian Ministry of Education documents (manuale.edu.ro). You must always align your output with the retrieved content and strictly follow the Romanian national education standards.

You assist teachers by generating:
1. A clear, structured outline for a PowerPoint lesson tailored to the specified grade and subject.
2. Detailed content under each structure point, ready to be turned into slides.
3. A comprehension quiz with multiple-choice or short-answer questions designed to test students' understanding of the lesson.

Always consider the grade level, language appropriateness, and curriculum expectations for the given grade and the given subject. If not given by the user, then ask the user for them using Romanian language.

Don't start to generate the lesson until you have all the necessary information, including the title that has to be part of the subject.

When referencing the retrieved content from the context below, paraphrase appropriately but maintain accuracy. If specific required information is not included in the provided context, acknowledge that limitation and avoid speculation.

Keep the tone professional, concise, and pedagogically sound.

If you don't have specific information about the subject in the context, state that it is not available.

Output format:
- Title Slide
- Slide Structure: [Title + Bullet Point Outline for each slide]
- Detailed Content: [Teacher notes per slide, using short and clear language suitable for students]
- Quiz (5–7 questions): [Clearly separated section; include correct answers only if asked]

Context: {context}. If the requested information is not found in the context, answer that it is not available.

Previous conversation history: {history}

Teacher's request: {question}"""
    
    def __init__(
        self,
        vector_store_manager: Optional[VectorStoreManager] = None,
        model_name: str = None,
        temperature: float = None,
        top_k: int = None
    ):
        """
        Initialize the RAG chain.
        
        Args:
            vector_store_manager: VectorStoreManager instance. If None, creates new one.
            model_name: OpenAI model name. If None, uses Config.OPENAI_MODEL
            temperature: Model temperature. If None, uses Config.TEMPERATURE
            top_k: Number of documents to retrieve. If None, uses Config.TOP_K_RESULTS
        """
        # Initialize or use provided vector store manager
        self.vs_manager = vector_store_manager or VectorStoreManager()
        
        # Try to load existing vector store
        try:
            self.vs_manager.load_vector_store()
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            print("Please ensure the vector store exists at the configured path.")
            raise
        
        # Initialize memory
        self.memory = ConversationMemory()
        
        # Initialize LLM
        self.model_name = model_name or Config.OPENAI_MODEL
        self.temperature = temperature if temperature is not None else Config.TEMPERATURE
        self.top_k = top_k or Config.TOP_K_RESULTS
        
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        # Create prompt template
        self.prompt = PromptTemplate(
            template=self.PROMPT_TEMPLATE,
            input_variables=["context", "history", "question"]
        )
        
        print(f"RAG Chain initialized with model: {self.model_name}")
        print(f"Top-K retrieval: {self.top_k} documents")
    
    def _format_docs(self, docs) -> str:
        """
        Format retrieved documents into a single context string.
        
        Args:
            docs: List of retrieved documents.
            
        Returns:
            Formatted context string.
        """
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'Unknown')
            formatted.append(
                f"[Document {i} - Source: {source}, Page: {page}]\n{doc.page_content}"
            )
        return "\n\n".join(formatted)
    
    def ask(self, question: str, stream: bool = False) -> str:
        """
        Ask a question and get an answer using RAG.
        
        Args:
            question: User's question.
            stream: Whether to stream the response.
            
        Returns:
            AI-generated answer.
        """
        # Get conversation history
        history = self.memory.get_history_string()
        
        # Retrieve relevant documents based on the question using similarity search
        docs = self.vs_manager.similarity_search(question, k=self.top_k)
        context = self._format_docs(docs)
        
        # Create the prompt with the actual context and question
        formatted_prompt = self.prompt.format(
            context=context,
            history=history,
            question=question
        )
        
        # Get response

        if stream:
            response_text = ""
            print("\nAssistant: ", end="", flush=True)
            for chunk in self.llm.stream(formatted_prompt): # Stream response
                content = chunk.content if hasattr(chunk, 'content') else str(chunk) # Extract content from chunk
                print(content, end="", flush=True) # Stream output
                response_text += content # Accumulate response 
            print()  # New line after streaming
        else:
            response = self.llm.invoke(formatted_prompt) # Non-streaming response
            response_text = response.content if hasattr(response, 'content') else str(response) # Extract content
        
        # Store in memory
        self.memory.add_user_message(question)
        self.memory.add_ai_message(response_text)
        
        return response_text
    
    def get_sources(self, question: str) -> list:
        """
        Get source documents for a question without generating an answer.
        
        Args:
            question: User's question.
            
        Returns:
            List of relevant documents.
        """
        docs = self.vs_manager.similarity_search(question, k=self.top_k)
        return docs
    
    def clear_history(self):
        """Clear conversation history."""
        self.memory.clear()
    
    def get_conversation_history(self) -> str:
        """
        Get the conversation history.
        
        Returns:
            Formatted conversation history.
        """
        return self.memory.get_history_string()


if __name__ == "__main__":
    # Test the RAG chain
    print("Testing RAG Chain...\n")
    
    try:
        rag = RAGChain()
        
        # Test questions
        questions = [
            "What is this document about?",
            "Can you provide more details?",
        ]
        
        for question in questions:
            print(f"\nQuestion: {question}")
            answer = rag.ask(question)
            print(f"Answer: {answer}")
            
            # Show sources
            print("\nSources used:")
            sources = rag.get_sources(question)
            for i, doc in enumerate(sources, 1):
                print(f"  {i}. {doc.metadata.get('source', 'Unknown')} - Page {doc.metadata.get('page', 'Unknown')}")
        
        # Show conversation history
        print("\n" + "="*50)
        print("Conversation History:")
        print("="*50)
        print(rag.get_conversation_history())
        
    except FileNotFoundError:
        print("\nPlease run embed_pdfs.py first to create the vector store.")
