# Romanian Education RAG System - Flask API

A Flask-based REST API that uses Retrieval-Augmented Generation (RAG) to create personalized educational materials for Romanian teachers. The system generates lecture content aligned with the Romanian Ministry of Education curriculum standards.

## 🚀 Features

- **AI-Powered Question Generation**: Generates clarifying questions based on pedagogical best practices
- **Dual-Version Lecture Creation**: Creates both student-friendly and teacher-enhanced versions of lectures
- **RAG Integration**: Uses ChromaDB vector store with curriculum documents to ensure accurate, curriculum-aligned content
- **Metadata Filtering**: Filters content by subject and grade level for precision
- **HTML Output**: Returns formatted HTML ready for frontend rendering

## 📋 API Endpoints

### 1. Generate Questions
`POST /api/generate-questions`

Generates 5-8 clarifying questions to gather information for creating high-quality lessons.

**Request:**
```json
{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "Biologie",
  "grade": 6
}
```

**Response:** Questions with multiple-choice or yes/no options

### 2. Generate Lecture
`POST /api/generate-lecture`

Generates comprehensive lecture materials in two HTML versions:
- **Student Version**: Age-appropriate, comprehensive learning material
- **Teacher Version**: Enhanced with teaching notes, advanced information, and pedagogical guidance

**Request:**
```json
{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "biologie",
  "grade": 6,
  "questions": [...],
  "answers": {"1": "answer1", "2": "answer2"}
}
```

**Response:** HTML-formatted student and teacher versions

See [API_EXAMPLES.md](API_EXAMPLES.md) for detailed examples with cURL and JavaScript.

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- ChromaDB vector store with embedded curriculum documents

### Setup Steps

1. **Clone the repository** (if not already done)

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
   
   Copy `.env.example` to `.env` and fill in your settings:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small
   VECTOR_STORE_PATH=./vectorstore
   CHROMA_COLLECTION_NAME=hackathon_collection
   ```

4. **Ensure vector store exists:**
   
   Make sure you have a ChromaDB vector store at `./vectorstore/` with:
   - Embedded curriculum documents
   - Metadata fields: `subject` (lowercase) and `grade` (integer)

5. **Run the Flask server:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📁 Project Structure

```
.
├── app.py                  # Flask application with API endpoints
├── questions_service.py    # Service for generating clarifying questions
├── lecture_service.py      # Service for generating lecture materials
├── vector_store.py         # ChromaDB vector store manager
├── config.py              # Configuration management
├── memory.py              # Conversation memory (not used in API)
├── rag_chain.py           # Original RAG chain (console version)
├── main.py                # Original console interface (deprecated)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example          # Environment variables template
├── API_EXAMPLES.md       # Detailed API usage examples
└── vectorstore/          # ChromaDB persistent storage
    └── chroma.sqlite3
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model for text generation | `gpt-4o-mini` |
| `OPENAI_EMBEDDING_MODEL` | Model for embeddings | `text-embedding-3-small` |
| `VECTOR_STORE_PATH` | Path to ChromaDB storage | `./vectorstore` |
| `CHROMA_COLLECTION_NAME` | ChromaDB collection name | `hackathon_collection` |
| `TOP_K_RESULTS` | Number of documents to retrieve | `8` |
| `TEMPERATURE` | Model temperature | `0.1` |

### Vector Store Metadata Requirements

Your ChromaDB vector store documents must have the following metadata:
- `subject`: Subject name in lowercase (e.g., "biologie", "matematică", "fizică")
- `grade`: Integer grade level (1-12)
- `source`: Document source (optional)
- `page`: Page number (optional)

## 🧪 Testing

### Test Questions Generation
```bash
python questions_service.py
```

### Test Lecture Generation
```bash
python lecture_service.py
```

### Test Full API
```bash
# Start the server
python app.py

# In another terminal, test with curl:
curl -X POST http://localhost:5000/api/generate-questions \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Lecture", "subject": "Biologie", "grade": 6}'
```

## 📖 Usage Workflow

1. **Frontend calls `/api/generate-questions`** with lecture parameters
2. **Display questions to teacher** and collect their answers
3. **Frontend calls `/api/generate-lecture`** with parameters + questions + answers
4. **Render HTML responses** in student and teacher views

See [API_EXAMPLES.md](API_EXAMPLES.md) for complete code examples.

## 🎨 Frontend Integration

### Rendering HTML
```javascript
// Both versions return HTML that can be rendered directly
document.getElementById('student-content').innerHTML = data.student_version;
document.getElementById('teacher-content').innerHTML = data.teacher_version;
```

### Styling Teacher Notes
```css
.teacher-note {
  background-color: #fff3cd;
  border-left: 4px solid #ffc107;
  padding: 10px;
  margin: 15px 0;
  font-style: italic;
}

.emphasis {
  font-weight: bold;
  color: #d32f2f;
}
```

## ⚡ Performance Notes

- **Question generation**: ~5-10 seconds
- **Lecture generation**: ~10-20 seconds (generates two versions)
- Both endpoints use OpenAI API, so response times depend on API availability
- Implement loading indicators in your frontend

## 🔒 Security Considerations

- **CORS**: Currently enabled for all origins. Restrict in production:
  ```python
  CORS(app, origins=['https://your-frontend-domain.com'])
  ```
- **API Key**: Never commit `.env` file to version control
- **Input Validation**: All endpoints validate required parameters
- **HTML Sanitization**: Consider sanitizing HTML in frontend if needed

## 🐛 Troubleshooting

### Server won't start
- Check that `.env` file exists with valid `OPENAI_API_KEY`
- Verify vector store exists at configured path
- Ensure all dependencies are installed

### "Vector store not found" error
- Confirm `./vectorstore/chroma.sqlite3` exists
- Check `VECTOR_STORE_PATH` in `.env`
- Verify collection name matches configuration

### Empty or irrelevant results
- Check that documents have correct metadata (`subject` and `grade`)
- Verify metadata filters match your data (subject should be lowercase)
- Increase `TOP_K_RESULTS` to retrieve more documents

### Dependencies installation fails
- Use Python 3.8 or higher
- Try: `pip install --upgrade pip`
- Install individually if needed: `pip install flask flask-cors langchain langchain-openai chromadb`

## 📝 License

This project is for educational purposes as part of the Adobe Hackathon.

## 🤝 Contributing

This is a hackathon project. For production use, consider:
- Adding authentication/authorization
- Implementing rate limiting
- Adding response caching
- Enhancing error handling
- Adding logging and monitoring
- Writing comprehensive tests

## 📞 Support

For issues or questions, refer to:
- [API_EXAMPLES.md](API_EXAMPLES.md) for usage examples
- [QUICKSTART.md](QUICKSTART.md) for original console version documentation
- Check logs in terminal where Flask server is running
