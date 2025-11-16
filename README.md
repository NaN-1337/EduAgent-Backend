# RAG Chatbot for Romanian Education

A Retrieval-Augmented Generation (RAG) chatbot that generates educational materials for Romanian teachers using OpenAI's GPT models and ChromaDB vector storage with pre-embedded curriculum documents.

## Features

- 📄 Uses pre-embedded Romanian curriculum documents from manuale.edu.ro
- 🔍 Local vector storage using ChromaDB
- 💬 Interactive chat interface with conversation memory
- 🧠 Context-aware responses using RAG
- 🎓 Generates lesson plans, PowerPoint outlines, and comprehension quizzes
- 📊 Document source tracking
- 🔄 Streaming responses

## Architecture

The system consists of:

1. **Vector Store (ChromaDB)**: Pre-embedded curriculum documents (already set up)
2. **Memory**: Conversation history management
3. **RAG Chain**: Combines retrieval with GPT-4o-mini for curriculum-aligned answers
4. **Educational Prompt**: Specialized for generating Romanian educational materials

## Installation

### 1. Clone or download this project

```bash
cd "Hackathon Adobe"
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
copy .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-api-key-here
```

## Usage

The vector store with embedded curriculum documents is already set up. Simply start the chatbot:

```bash
python main.py
```

### Available Commands

In the chatbot:
- Type your request to generate educational materials
- `sources` - Show source documents for the last question
- `history` - Show conversation history
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the chatbot

### Example Requests

```
You: Generate a lesson plan for grade 6 biology about photosynthesis
You: Create a PowerPoint outline about cells and their structure
You: Make a quiz about plant life cycles for grade 6
```

The system will generate:
- **Title Slide** with appropriate subject and grade level
- **Slide Structure** with bullet point outlines
- **Detailed Content** ready for PowerPoint slides
- **Comprehension Quiz** with 5-7 questions

## Configuration

Edit `.env` to customize settings:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.1

# Paths
VECTOR_STORE_PATH=./vectorstore
CHROMA_COLLECTION_NAME=hackathon_collection

# Retrieval
TOP_K_RESULTS=4
```

## Project Structure

```
Hackathon Adobe/
├── config.py              # Configuration management
├── vector_store.py        # ChromaDB vector store management
├── memory.py              # Conversation memory
├── rag_chain.py           # RAG pipeline implementation
├── main.py                # Interactive chatbot
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
└── vectorstore/          # Pre-embedded curriculum documents
    └── chroma.sqlite3    # ChromaDB database
```

## How It Works

1. **Document Retrieval**: User request is embedded and used to find relevant curriculum chunks
2. **Context Building**: Retrieved chunks + conversation history form the context
3. **Response Generation**: GPT-4o-mini generates curriculum-aligned educational materials
4. **Educational Format**: Output is structured for immediate use by teachers

## Notes

- Vector store is pre-populated with Romanian curriculum documents
- All data stays on your machine (except OpenAI API calls)
- Requires OpenAI API key for embeddings and chat completions
- Designed for Romanian Ministry of Education curriculum standards

## License

MIT License - Feel free to use and modify as needed.
