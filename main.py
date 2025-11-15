"""
Main entry point for the RAG chatbot.
Interactive chat interface for asking questions about your PDF documents.
"""
import sys
from rag_chain import RAGChain
from config import Config


def print_welcome():
    """Print welcome message."""
    print("="*60)
    print("  RAG Chatbot - Ask questions about your PDF documents")
    print("="*60)
    print(f"Model: {Config.OPENAI_MODEL}")
    print(f"Embedding: {Config.OPENAI_EMBEDDING_MODEL}")
    print("\nCommands:")
    print("  - Type your question to get an answer")
    print("  - 'sources' - Show sources for the last question")
    print("  - 'history' - Show conversation history")
    print("  - 'clear' - Clear conversation history")
    print("  - 'quit' or 'exit' - Exit the chatbot")
    print("="*60 + "\n")


def main():
    """Main function to run the interactive chatbot."""
    
    # Print welcome message
    print_welcome()
    
    # Initialize RAG chain
    try:
        print("Initializing RAG system...")
        rag = RAGChain()
        print("✓ RAG system ready!\n")
    except FileNotFoundError:
        print("\n❌ Error: Vector store not found!")
        print("Please run 'python embed_pdfs.py' first to create the vector store.")
        print("Make sure you have PDF files in the './pdfs' directory.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error initializing RAG system: {e}")
        sys.exit(1)
    
    last_question = None
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye! 👋")
                break
            
            elif user_input.lower() == 'clear':
                rag.clear_history()
                last_question = None
                continue
            
            elif user_input.lower() == 'history':
                print("\n" + "="*60)
                print("Conversation History:")
                print("="*60)
                history = rag.get_conversation_history()
                print(history if history != "No previous conversation." else "No conversation history yet.")
                print("="*60 + "\n")
                continue
            
            elif user_input.lower() == 'sources':
                if not last_question:
                    print("No previous question to show sources for.\n")
                    continue
                
                print(f"\nSources for: '{last_question}'")
                print("-" * 60)
                sources = rag.get_sources(last_question)
                for i, doc in enumerate(sources, 1):
                    source = doc.metadata.get('source', 'Unknown')
                    page = doc.metadata.get('page', 'Unknown')
                    print(f"\n{i}. {source} (Page {page})")
                    print(f"   Preview: {doc.page_content[:200]}...")
                print("-" * 60 + "\n")
                continue
            
            # Regular question
            last_question = user_input
            
            print("\nAssistant: ", end="", flush=True)
            
            # Get answer with streaming
            answer = rag.ask(user_input, stream=True)
            
            print()  # New line after answer
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            continue


if __name__ == "__main__":
    main()
