# Flask API Testing Guide

## Setup Complete! ✅

Your RAG system has been successfully refactored into a Flask backend API.

## 📁 New Files Created

1. **app.py** - Main Flask application with two API endpoints
2. **questions_service.py** - Service to generate clarifying questions
3. **lecture_service.py** - Service to generate student and teacher lecture versions
4. **API_EXAMPLES.md** - Comprehensive API documentation with request/response examples
5. **README_API.md** - Complete API setup and usage guide

## 🔄 Modified Files

1. **requirements.txt** - Added Flask and Flask-CORS dependencies
2. **vector_store.py** - Added metadata filtering support to `similarity_search()` method

## 🚀 How to Start the Server

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt

# Start the Flask server
python app.py
```

The API will be available at: `http://localhost:5000`

## 📡 Available Endpoints

### 1. Health Check
```
GET /api/health
```

### 2. Generate Questions
```
POST /api/generate-questions
Content-Type: application/json

{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "Biologie",
  "grade": 6
}
```

**Response:** JSON with 5-8 clarifying questions

### 3. Generate Lecture
```
POST /api/generate-lecture
Content-Type: application/json

{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "biologie",
  "grade": 6,
  "questions": [...from first endpoint...],
  "answers": {
    "1": "Introducerea conceptelor noi",
    "2": "50 minute (o oră)"
  }
}
```

**Response:** JSON with `student_version` and `teacher_version` in HTML format

## 🧪 Testing the API

### Using cURL:

```bash
# Test health check
curl http://localhost:5000/api/health

# Test generate questions
curl -X POST http://localhost:5000/api/generate-questions \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Fotosinteza\", \"subject\": \"Biologie\", \"grade\": 7}"

# Test generate lecture
curl -X POST http://localhost:5000/api/generate-lecture \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Fotosinteza\", \"subject\": \"biologie\", \"grade\": 7, \"questions\": [{\"id\": 1, \"question\": \"Test?\"}], \"answers\": {\"1\": \"Da\"}}"
```

### Using Python:

```python
import requests

# Generate questions
response = requests.post('http://localhost:5000/api/generate-questions', 
    json={
        'title': 'Fotosinteza',
        'subject': 'Biologie',
        'grade': 7
    })
questions_data = response.json()
print(questions_data)

# Generate lecture
response = requests.post('http://localhost:5000/api/generate-lecture',
    json={
        'title': 'Fotosinteza',
        'subject': 'biologie',
        'grade': 7,
        'questions': questions_data['data']['questions'],
        'answers': {
            '1': 'Introducerea conceptelor noi',
            '2': '50 minute (o oră)'
        }
    })
lecture_data = response.json()
print(lecture_data['data']['student_version'])
print(lecture_data['data']['teacher_version'])
```

## 🔍 Important Notes

### Vector Store Metadata
The ChromaDB vector store **must** have documents with these metadata fields:
- `subject` (string, lowercase): e.g., "biologie", "matematică", "fizică"
- `grade` (int): 1-12

Example metadata filtering in endpoint 2:
```python
filter={
    "$and": [
        {"subject": "biologie"},
        {"grade": 6}
    ]
}
```

### Response Times
- **Questions endpoint**: ~5-10 seconds
- **Lecture endpoint**: ~10-20 seconds (generates 2 versions)

Both endpoints make OpenAI API calls, so show loading indicators in your frontend!

### HTML Output
Both lecture versions are returned as HTML strings with basic styling:
- Student version: Clean, age-appropriate content
- Teacher version: Enhanced with `<div class="teacher-note">` annotations

You can render them directly in your frontend:
```javascript
document.getElementById('student-content').innerHTML = data.student_version;
document.getElementById('teacher-content').innerHTML = data.teacher_version;
```

### CSS for Teacher Notes
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

## 📚 Complete Documentation

See **API_EXAMPLES.md** for:
- Detailed request/response examples
- JavaScript/fetch examples
- Complete workflow demonstrations
- Error handling best practices

See **README_API.md** for:
- Full setup instructions
- Configuration details
- Troubleshooting guide
- Security considerations

## ⚠️ If Flask Import Error Occurs

If you see `ModuleNotFoundError: No module named 'flask'`, try:

```bash
# Option 1: Use python -m pip
python -m pip install flask flask-cors

# Option 2: Reinstall all requirements
python -m pip install -r requirements.txt

# Option 3: Check Python path
python -c "import sys; print(sys.executable)"
python -m site
```

## 🎯 Next Steps

1. **Start the server**: `python app.py`
2. **Test endpoints**: Use curl or Postman to test the API
3. **Integrate with frontend**: Use the examples in API_EXAMPLES.md
4. **Deploy**: Consider using Gunicorn for production

## 🤝 Frontend Integration Checklist

- [ ] Test `/api/health` endpoint
- [ ] Implement questions form in frontend
- [ ] Collect teacher answers for all questions
- [ ] Send complete payload to `/api/generate-lecture`
- [ ] Render HTML responses in UI
- [ ] Add loading indicators for API calls
- [ ] Implement error handling
- [ ] Style teacher notes sections

---

**Your RAG system is now a production-ready REST API!** 🎉

For any questions or issues, refer to the detailed documentation in:
- API_EXAMPLES.md
- README_API.md
