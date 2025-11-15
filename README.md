# RAG Chatbot with LangChain

A Retrieval-Augmented Generation (RAG) chatbot that allows you to ask questions about your PDF documents using OpenAI's GPT models and local FAISS vector storage.

## Features

- 📄 Load and process multiple PDF documents
- 🔍 Local vector storage using FAISS (no cloud database required)
- 💬 Interactive chat interface with conversation memory
- 🧠 Context-aware responses using RAG
- 📊 Document source tracking
- 🔄 Streaming responses

## Architecture

Based on the LangChain flow with the following components:

1. **File Loader**: Loads PDF documents from local directory
2. **Text Splitter**: Chunks documents for optimal embedding
3. **Vector Store**: FAISS with OpenAI embeddings (local storage)
4. **Memory**: Conversation history management
5. **RAG Chain**: Combines retrieval with GPT-4o-mini for answers
6. **Prompt Template**: Contextual prompt engineering

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

### Step 1: Prepare Your PDFs

Place your PDF documents in the `./pdfs` directory:

```bash
mkdir pdfs
# Copy your PDF files to the pdfs directory
```

### Step 2: Create the Vector Store

Run the embedding script to process your PDFs and create the local vector store:

```bash
python embed_pdfs.py
```

This will:
- Load all PDF files from `./pdfs`
- Split them into chunks
- Create embeddings using OpenAI
- Store them locally in `./vector_store`

### Step 3: Start the Chatbot

Run the main script to start the interactive chat:

```bash
python main.py
```

### Available Commands

In the chatbot:
- Type your question to get an answer
- `sources` - Show source documents for the last question
- `history` - Show conversation history
- `clear` - Clear conversation history
- `quit` or `exit` - Exit the chatbot

## Configuration

Edit `.env` to customize settings:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.1

# Paths
PDF_DIRECTORY=./pdfs
VECTOR_STORE_PATH=./vector_store

# Text Splitting
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Retrieval
TOP_K_RESULTS=4
```

## Project Structure

```
Hackathon Adobe/
├── config.py              # Configuration management
├── pdf_loader.py          # PDF document loading
├── text_splitter.py       # Document chunking
├── vector_store.py        # FAISS vector store management
├── memory.py              # Conversation memory
├── rag_chain.py           # RAG pipeline implementation
├── embed_pdfs.py          # Script to embed PDFs
├── main.py                # Interactive chatbot
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
└── pdfs/                  # Directory for PDF files
    └── (your PDF files)
```

## How It Works

1. **Document Processing**: PDFs are loaded and split into manageable chunks
2. **Embedding**: Each chunk is embedded using OpenAI's embedding model
3. **Vector Storage**: Embeddings are stored locally in FAISS for fast retrieval
4. **Query Processing**: User questions are embedded and used to find relevant chunks
5. **Context Building**: Retrieved chunks + conversation history form the context
6. **Response Generation**: GPT-4o-mini generates an answer based on the context

## Example Session

```
You: What is this document about?
Assistant: Based on the documents, this appears to be about...

You: Can you provide more details?
Assistant: Certainly! Building on the previous context...

You: sources
Sources for: 'Can you provide more details?'
1. document.pdf (Page 3)
   Preview: This section discusses...
```

## Troubleshooting

### "Vector store not found"
Run `python embed_pdfs.py` first to create the vector store.

### "No PDF files found"
Make sure you have PDF files in the `./pdfs` directory.

### "OPENAI_API_KEY not found"
Create a `.env` file with your OpenAI API key (see `.env.example`).

## Notes

- Vector store is created locally (no Astra DB or cloud dependencies)
- All data stays on your machine
- Requires OpenAI API key for embeddings and chat completions
- First-time embedding may take a few minutes depending on document size

## License

MIT License - Feel free to use and modify as needed.
