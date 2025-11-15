# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Your OpenAI API Key
Edit the `.env` file and add your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Add PDF Files
Copy your PDF documents to the `pdfs` folder:
```
pdfs/
  └── your-document.pdf
```

## Run the Chatbot

### First Time: Embed Your PDFs
```bash
python embed_pdfs.py
```
This creates a local vector store from your PDFs (takes a few minutes).

### Start Chatting
```bash
python main.py
```

## Example Interaction

```
You: What is this document about?
Assistant: [AI provides answer based on your PDFs]

You: Can you elaborate on that?
Assistant: [AI provides detailed answer with context]

You: sources
[Shows which PDF pages were used to answer]

You: quit
```

## Tips

- The chatbot remembers conversation history
- Use `clear` to start a fresh conversation
- Use `sources` to see which documents were referenced
- Add more PDFs anytime and re-run `embed_pdfs.py`

## Need Help?

See `README.md` for full documentation.
