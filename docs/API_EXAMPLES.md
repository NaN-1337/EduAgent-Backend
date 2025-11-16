# API Examples - Romanian Education RAG System

This document provides request and response examples for both API endpoints.

## Base URL
```
http://localhost:5000
```

---

## 1. Generate Questions Endpoint

**Endpoint:** `POST /api/generate-questions`

This endpoint analyzes the lecture parameters and generates clarifying questions that help gather information needed to create high-quality educational content.

### Request

**URL:** `http://localhost:5000/api/generate-questions`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "Biologie",
  "grade": 6
}
```

**Field Descriptions:**
- `title` (string, required): The title or topic of the lecture
- `subject` (string, required): The subject name (e.g., "Matematică", "Biologie", "Istorie")
- `grade` (int, required): The grade level (1-12)

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "question": "Care este scopul principal al lecției?",
        "type": "single-choice",
        "options": [
          "Introducerea conceptelor noi",
          "Aprofundarea cunoștințelor existente",
          "Pregătirea pentru evaluare",
          "Altele"
        ]
      },
      {
        "id": 2,
        "question": "Cât timp este alocat pentru această lecție?",
        "type": "single-choice",
        "options": [
          "30 minute",
          "45 minute",
          "50 minute (o oră)",
          "100 minute (două ore)",
          "Altele"
        ]
      },
      {
        "id": 3,
        "question": "Elevii au cunoștințe prealabile despre structura celulei?",
        "type": "yes-no",
        "options": [
          "Da",
          "Nu"
        ]
      },
      {
        "id": 4,
        "question": "Ce metode didactice preferați să utilizați?",
        "type": "single-choice",
        "options": [
          "Prezentare frontală cu explicații",
          "Activități practice și experimente",
          "Lucru în grup",
          "Învățare prin descoperire",
          "Altele"
        ]
      },
      {
        "id": 5,
        "question": "Aveți acces la mijloace didactice specifice (microscop, modele)?",
        "type": "yes-no",
        "options": [
          "Da",
          "Nu"
        ]
      },
      {
        "id": 6,
        "question": "Care sunt aspectele pe care doriți să le evidențiați?",
        "type": "single-choice",
        "options": [
          "Structura celulei",
          "Funcțiile celulare",
          "Diferențele între celula animală și vegetală",
          "Toate aspectele în mod echilibrat",
          "Altele"
        ]
      },
      {
        "id": 7,
        "question": "Cum doriți să evaluați înțelegerea elevilor?",
        "type": "single-choice",
        "options": [
          "Quiz cu întrebări cu variante multiple",
          "Întrebări deschise",
          "Activitate practică",
          "Discuții în clasă",
          "Altele"
        ]
      }
    ]
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: title, subject, and grade are required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: [error details]"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-questions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Celula - unitatea structurală și funcțională a vieții",
    "subject": "Biologie",
    "grade": 6
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-questions', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Celula - unitatea structurală și funcțională a vieții',
    subject: 'Biologie',
    grade: 6
  })
})
  .then(response => response.json())
  .then(data => {
    console.log('Questions:', data.data.questions);
  })
  .catch(error => console.error('Error:', error));
```

---

## 2. Generate Lecture Endpoint

**Endpoint:** `POST /api/generate-lecture`

This endpoint generates comprehensive lecture materials in two versions: one for students and an enhanced version for teachers. It uses RAG (Retrieval-Augmented Generation) to pull relevant content from the curriculum documents and filters by subject and grade.

### Request

**URL:** `http://localhost:5000/api/generate-lecture`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "title": "Celula - unitatea structurală și funcțională a vieții",
  "subject": "biologie",
  "grade": 6,
  "questions": [
    {
      "id": 1,
      "question": "Care este scopul principal al lecției?",
      "type": "single-choice",
      "options": ["Introducerea conceptelor noi", "Aprofundarea cunoștințelor existente", "Pregătirea pentru evaluare", "Altele"]
    },
    {
      "id": 2,
      "question": "Cât timp este alocat pentru această lecție?",
      "type": "single-choice",
      "options": ["30 minute", "45 minute", "50 minute (o oră)", "100 minute (două ore)", "Altele"]
    },
    {
      "id": 3,
      "question": "Elevii au cunoștințe prealabile despre structura celulei?",
      "type": "yes-no",
      "options": ["Da", "Nu"]
    }
  ],
  "answers": {
    "1": "Introducerea conceptelor noi",
    "2": "50 minute (o oră)",
    "3": "Nu"
  }
}
```

**Field Descriptions:**
- `title` (string, required): The title or topic of the lecture
- `subject` (string, required): The subject name in lowercase (e.g., "matematică", "biologie", "istorie") - used for vector store filtering
- `grade` (int, required): The grade level (1-12) - used for vector store filtering
- `questions` (array, required): The questions array returned from the first endpoint
- `answers` (object, required): Dictionary mapping question IDs (as strings) to the selected answers

**Important Notes:**
- The `subject` field should match the metadata in your vector store (typically lowercase)
- The `answers` keys must match the question `id` values (converted to strings)
- For "Other" options, the teacher can provide custom text as the answer value

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule. <strong>Celula</strong> este considerată unitatea structurală și funcțională a vieții deoarece toate procesele vitale au loc la nivel celular.</p>\n\n<h2>Structura celulei</h2>\n<p>Fiecare celulă este formată din mai multe componente importante:</p>\n<ul>\n  <li><strong>Membrana celulară</strong> - învelișul exterior care protejează celula și controlează ce intră și iese din ea</li>\n  <li><strong>Citoplasma</strong> - substanța gelatinoasă din interiorul celulei unde se desfășoară majoritatea proceselor vitale</li>\n  <li><strong>Nucleul</strong> - centrul de comandă al celulei, care conține materialul genetic (ADN)</li>\n</ul>\n\n<h3>Celula animală vs. Celula vegetală</h3>\n<p>Există două tipuri principale de celule:</p>\n<ol>\n  <li><strong>Celula animală</strong> - nu are perete celular, are forme variate</li>\n  <li><strong>Celula vegetală</strong> - are perete celular rigid, conține cloroplaste pentru fotosinteză</li>\n</ol>\n\n<h2>Funcțiile celulare</h2>\n<p>Celulele îndeplinesc mai multe funcții esențiale pentru viață:</p>\n<ul>\n  <li><em>Nutriția</em> - celula obține și procesează substanțele nutritive</li>\n  <li><em>Respirația celulară</em> - procesul prin care celula obține energie</li>\n  <li><em>Reproducerea</em> - celulele se pot divide pentru a forma celule noi</li>\n  <li><em>Eliminarea deșeurilor</em> - celula elimină substanțele de care nu mai are nevoie</li>\n</ul>\n\n<h2>Concluzie</h2>\n<p>Înțelegerea celulei este fundamentală pentru biologie, deoarece toate organismele vii sunt formate din celule. Fiecare celulă funcționează ca o mică fabrică care menține viața.</p>",
    
    "teacher_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Această lecție este concepută pentru clasa a 6-a, cu durată de 50 minute. Elevii nu au cunoștințe prealabile despre structura celulei, așa că este important să începeți cu elemente de bază și să utilizați multe exemple vizuale. Sugerăm alocarea timpului astfel: 10 min introducere, 25 min partea principală, 10 min activități practice, 5 min recapitulare.]</div>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule. <strong>Celula</strong> este considerată unitatea structurală și funcțională a vieții deoarece toate procesele vitale au loc la nivel celular.</p>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Începeți cu o analogie simplă - comparați celula cu o cameră dintr-o casă sau cu o clasă. Fiecare cameră/clasă are pereți, conținut și îndeplinește funcții specifice. Această analogie îi ajută pe elevi să înțeleagă conceptul de unitate funcțională. Întrebați elevii: \"Ce lucruri vii cunoașteți?\" și explicați că toate sunt formate din celule - de la bacterii (o singură celulă) până la oameni (trilioane de celule).]</div>\n\n<h2>Structura celulei</h2>\n<p>Fiecare celulă este formată din mai multe componente importante:</p>\n<ul>\n  <li><strong>Membrana celulară</strong> - învelișul exterior care protejează celula și controlează ce intră și iese din ea</li>\n  <li><strong>Citoplasma</strong> - substanța gelatinoasă din interiorul celulei unde se desfășoară majoritatea proceselor vitale</li>\n  <li><strong>Nucleul</strong> - centrul de comandă al celulei, care conține materialul genetic (ADN)</li>\n</ul>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Aici este esențial să folosiți <span class=\"emphasis\">diagrame mari și clare</span>. Dacă aveți acces la un microscop, ar fi ideal să arătați elevilor celule reale (de exemplu, celule din epiderma cepei). Concept cheie de subliniat: membrana celulară funcționează ca un filtru selectiv - nu orice poate intra sau ieși. Citoplasmă provine din grecescul \"kytos\" (celulă) și \"plasma\" (formă). O concepție greșită frecventă: elevii cred că nucleul este în centrul geometric al celulei - explicați că poziția variază.]</div>\n\n<h3>Celula animală vs. Celula vegetală</h3>\n<p>Există două tipuri principale de celule:</p>\n<ol>\n  <li><strong>Celula animală</strong> - nu are perete celular, are forme variate</li>\n  <li><strong>Celula vegetală</strong> - are perete celular rigid, conține cloroplaste pentru fotosinteză</li>\n</ol>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Comparația este esențială aici. Creați un tabel comparativ pe tablă cu caracteristicile comune și diferențele. <span class=\"emphasis\">Diferențe cheie de subliniat:</span> 1) Peretele celular (celuloză) face celula vegetală mai rigidă - de aceea plantele pot sta în picioare; 2) Cloroplastele (cu clorofilă verde) permit plantelor să producă propria hrană prin fotosinteză; 3) Vacuola mare centrală în celula vegetală stochează apă și nutrienți. Întrebare pentru discuție: \"De ce credeți că plantele sunt verzi?\" - legătura cu cloroplastele. Legătură interdisciplinară cu chimia: procesul de fotosinteză.]</div>\n\n<h2>Funcțiile celulare</h2>\n<p>Celulele îndeplinesc mai multe funcții esențiale pentru viață:</p>\n<ul>\n  <li><em>Nutriția</em> - celula obține și procesează substanțele nutritive</li>\n  <li><em>Respirația celulară</em> - procesul prin care celula obține energie</li>\n  <li><em>Reproducerea</em> - celulele se pot divide pentru a forma celule noi</li>\n  <li><em>Eliminarea deșeurilor</em> - celula elimină substanțele de care nu mai are nevoie</li>\n</ul>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Conceptul de <span class=\"emphasis\">funcție celulară</span> poate fi abstract pentru clasa a 6-a. Folosiți analogii cu viața de zi cu zi: Nutriția = \"celula mănâncă\"; Respirația = \"celula respiră pentru energie\"; Reproducerea = \"celula se copiază\"; Eliminare = \"celula duce gunoiul\". Important: respirația celulară ≠ respirația pulmonară - clarificați diferența. Respirația celulară se întâmplă în mitocondrii (organite despre care veți învăța mai târziu). Informație avansată pentru profesor: procesul complet de respirație celulară: C6H12O6 + 6O2 → 6CO2 + 6H2O + energie (ATP). Nu intrați în detalii chimice cu elevii de clasa a 6-a, dar păstrați corectitudinea științifică. Activitate sugerată: cereți elevilor să deseneze o celulă și să eticheteze componentele.]</div>\n\n<h2>Concluzie</h2>\n<p>Înțelegerea celulei este fundamentală pentru biologie, deoarece toate organismele vii sunt formate din celule. Fiecare celulă funcționează ca o mică fabrică care menține viața.</p>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: <span class=\"emphasis\">Recapitulare finală (5 minute)</span>: Puneți întrebări cheie: 1) Ce este celula? 2) Care sunt cele 3 componente principale? 3) Ce diferență există între celula animală și vegetală? Evaluare sugerată: Quiz de 5 minute cu 7 întrebări (conform preferințelor dumneavoastră). Temă pentru acasă: Desenați și etichetați o celulă animală și una vegetală. Lecția următoare: Vom explora mai în detaliu organitele celulare (mitocondrii, ribozomi, reticulul endoplasmatic). Resursă suplimentară recomandată: video educațional despre celulă din biblioteca școlii sau platforma educațională online.]</div>"
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.student_version` (string): HTML-formatted lecture content designed for students at the specified grade level
- `data.teacher_version` (string): Enhanced HTML-formatted content with teacher notes, advanced information, and teaching guidance

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: title, subject, grade, questions, and answers are required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: [error details]"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-lecture \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Celula - unitatea structurală și funcțională a vieții",
    "subject": "biologie",
    "grade": 6,
    "questions": [
      {
        "id": 1,
        "question": "Care este scopul principal al lecției?",
        "type": "single-choice",
        "options": ["Introducerea conceptelor noi", "Aprofundarea cunoștințelor existente"]
      },
      {
        "id": 2,
        "question": "Cât timp este alocat pentru această lecție?",
        "type": "single-choice",
        "options": ["30 minute", "50 minute (o oră)"]
      }
    ],
    "answers": {
      "1": "Introducerea conceptelor noi",
      "2": "50 minute (o oră)"
    }
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-lecture', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'Celula - unitatea structurală și funcțională a vieții',
    subject: 'biologie',
    grade: 6,
    questions: [
      {
        id: 1,
        question: 'Care este scopul principal al lecției?',
        type: 'single-choice',
        options: ['Introducerea conceptelor noi', 'Aprofundarea cunoștințelor existente']
      },
      {
        id: 2,
        question: 'Cât timp este alocat pentru această lecție?',
        type: 'single-choice',
        options: ['30 minute', '50 minute (o oră)']
      }
    ],
    answers: {
      '1': 'Introducerea conceptelor noi',
      '2': '50 minute (o oră)'
    }
  })
})
  .then(response => response.json())
  .then(data => {
    const studentHTML = data.data.student_version;
    const teacherHTML = data.data.teacher_version;
    
    // Render in your frontend
    document.getElementById('student-content').innerHTML = studentHTML;
    document.getElementById('teacher-content').innerHTML = teacherHTML;
  })
  .catch(error => console.error('Error:', error));
```

---

## Complete Workflow Example

Here's a complete workflow showing how to use both endpoints together:

### Step 1: Generate Questions
```javascript
// Step 1: Get clarifying questions
const questionsResponse = await fetch('http://localhost:5000/api/generate-questions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Fotosinteza',
    subject: 'Biologie',
    grade: 7
  })
});

const questionsData = await questionsResponse.json();
const questions = questionsData.data.questions;

// Display questions to teacher in UI and collect answers
// ... (UI interaction) ...
```

### Step 2: Generate Lecture with Answers
```javascript
// Step 2: Generate lecture with collected answers
const answers = {
  '1': 'Introducerea conceptelor noi',
  '2': '50 minute (o oră)',
  '3': 'Da',
  '4': 'Activități practice și experimente',
  '5': 'Da',
  '6': 'Procesul de fotosinteză',
  '7': 'Quiz cu întrebări cu variante multiple'
};

const lectureResponse = await fetch('http://localhost:5000/api/generate-lecture', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Fotosinteza',
    subject: 'biologie',
    grade: 7,
    questions: questions,
    answers: answers
  })
});

const lectureData = await lectureResponse.json();
const studentVersion = lectureData.data.student_version;
const teacherVersion = lectureData.data.teacher_version;

// Render both versions in your UI
document.getElementById('student-view').innerHTML = studentVersion;
document.getElementById('teacher-view').innerHTML = teacherVersion;
```

---

## Error Handling Best Practices

```javascript
async function generateLecture(title, subject, grade, questions, answers) {
  try {
    const response = await fetch('http://localhost:5000/api/generate-lecture', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, subject, grade, questions, answers })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Unknown error occurred');
    }
    
    const data = await response.json();
    return data.data;
    
  } catch (error) {
    console.error('Failed to generate lecture:', error);
    // Show error to user in UI
    showErrorMessage(error.message);
    return null;
  }
}
```

---

## 3. Generate Presentation Endpoint

**Endpoint:** `POST /api/generate-presentation`

This endpoint takes the student version content from the lecture generation endpoint and uses the Presenton API to create a PowerPoint presentation. It returns both the presentation file URL and the parsed content of each slide.

### Request

**URL:** `http://localhost:5000/api/generate-presentation`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule...</p>\n\n<h2>Structura celulei</h2>\n<p>Fiecare celulă este formată din mai multe componente importante...</p>",
  "n_slides": 8,
  "language": "Romanian",
  "template": "general",
  "tone": "educational",
  "verbosity": "standard",
  "export_as": "pptx",
  "image_type": "stock"
}
```

**Field Descriptions:**
- `student_version` (string, required): The HTML content from `/api/generate-lecture` endpoint
- `n_slides` (int, optional): Number of slides to generate (default: 8, range: 1-50)
- `language` (string, optional): Language for the presentation (default: "Romanian")
- `template` (string, optional): Template to use - options: "general", "modern", "standard", "swift" (default: "general")
- `tone` (string, optional): Tone for text - options: "default", "casual", "professional", "funny", "educational", "sales_pitch" (default: "educational")
- `verbosity` (string, optional): Text verbosity - options: "concise", "standard", "text-heavy" (default: "standard")
- `export_as` (string, optional): Export format - options: "pptx", "pdf" (default: "pptx")
- `image_type` (string, optional): Image type - options: "stock", "ai-generated" (default: "stock")
- `theme` (string, optional): Custom theme name (e.g., "edge-yellow", "light-rose", "mint-blue", "professional-blue", "professional-dark")

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "presentation": {
      "id": "d3000f96-096c-4768-b67b-e99aed029b57",
      "download_url": "https://api.presenton.ai/static/user_data/d3000f96-096c-4768-b67b-e99aed029b57/Celula.pptx",
      "edit_url": "https://presenton.ai/presentation?id=d3000f96-096c-4768-b67b-e99aed029b57",
      "credits_consumed": 8,
      "n_slides": 8,
      "language": "Romanian",
      "title": "Celula - unitatea structurală și funcțională a vieții"
    },
    "slides": [
      {
        "slide_index": 0,
        "layout": "title",
        "html_content": "<div class=\"slide-title\"><h1>Celula - unitatea structurală și funcțională a vieții</h1></div>",
        "speaker_note": "Slide de introducere pentru lecția despre celulă",
        "content": {
          "title": "Celula - unitatea structurală și funcțională a vieții",
          "subtitle": "Biologie - Clasa a 6-a"
        }
      },
      {
        "slide_index": 1,
        "layout": "content",
        "html_content": "<div class=\"slide-content\"><h2>Introducere</h2><p>Celula este cea mai mică unitate vie a organismelor...</p></div>",
        "speaker_note": "Explicați conceptul de celulă ca unitate fundamentală a vieții",
        "content": {
          "title": "Introducere",
          "body": "Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule.",
          "bullets": [
            "Celula = unitatea structurală",
            "Procesele vitale la nivel celular",
            "Toate organismele sunt formate din celule"
          ]
        }
      },
      {
        "slide_index": 2,
        "layout": "content",
        "html_content": "<div class=\"slide-content\"><h2>Structura celulei</h2><ul><li>Membrana celulară</li><li>Citoplasma</li><li>Nucleul</li></ul></div>",
        "speaker_note": "Prezentați cele trei componente principale ale celulei",
        "content": {
          "title": "Structura celulei",
          "body": "Fiecare celulă este formată din mai multe componente importante",
          "bullets": [
            "Membrana celulară - învelișul protector",
            "Citoplasma - substanța gelatinoasă",
            "Nucleul - centrul de comandă cu ADN"
          ]
        }
      }
    ]
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.presentation`: Object containing presentation metadata
  - `id`: UUID of the generated presentation
  - `download_url`: Direct download link for the .pptx or .pdf file
  - `edit_url`: Link to edit the presentation in Presenton's web interface
  - `credits_consumed`: Number of Presenton API credits used
  - `n_slides`: Total number of slides in the presentation
  - `language`: Language of the presentation
  - `title`: Title of the presentation
- `data.slides`: Array of parsed slide objects
  - `slide_index`: Position of the slide (0-indexed)
  - `layout`: Layout type of the slide (e.g., "title", "content", "two-column")
  - `html_content`: HTML representation of the slide content
  - `speaker_note`: Speaker notes for the slide
  - `content`: Structured content object with slide details (title, body, bullets, etc.)

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameter: student_version is required"
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "error": "Presenton service not configured. Please add PRESENTON_API_KEY to your .env file."
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: [error details]"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-presentation \
  -H "Content-Type: application/json" \
  -d '{
    "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1><h2>Introducere</h2><p>Celula este cea mai mică unitate vie...</p>",
    "n_slides": 8,
    "language": "Romanian",
    "tone": "educational"
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-presentation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    student_version: studentVersionHTML,  // From previous endpoint
    n_slides: 8,
    language: 'Romanian',
    template: 'modern',
    tone: 'educational',
    verbosity: 'standard',
    export_as: 'pptx'
  })
})
  .then(response => response.json())
  .then(data => {
    const downloadUrl = data.data.presentation.download_url;
    const editUrl = data.data.presentation.edit_url;
    const slides = data.data.slides;
    
    // Download the presentation
    window.open(downloadUrl, '_blank');
    
    // Or display slide previews in your UI
    slides.forEach(slide => {
      console.log(`Slide ${slide.slide_index}: ${slide.content.title}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

---

## Complete Workflow Example (All 3 Endpoints)

Here's a complete workflow showing how to use all three endpoints together:

### Step 1: Generate Questions
```javascript
// Step 1: Get clarifying questions
const questionsResponse = await fetch('http://localhost:5000/api/generate-questions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Celula - unitatea structurală și funcțională a vieții',
    subject: 'Biologie',
    grade: 6
  })
});

const questionsData = await questionsResponse.json();
const questions = questionsData.data.questions;

// Display questions to teacher in UI and collect answers
// ... (UI interaction) ...
```

### Step 2: Generate Lecture with Answers
```javascript
// Step 2: Generate lecture with collected answers
const answers = {
  '1': 'Introducerea conceptelor noi',
  '2': '50 minute (o oră)',
  '3': 'Da',
  '4': 'Activități practice și experimente'
};

const lectureResponse = await fetch('http://localhost:5000/api/generate-lecture', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Celula - unitatea structurală și funcțională a vieții',
    subject: 'biologie',
    grade: 6,
    questions: questions,
    answers: answers
  })
});

const lectureData = await lectureResponse.json();
const studentVersion = lectureData.data.student_version;
const teacherVersion = lectureData.data.teacher_version;
```

### Step 3: Generate PowerPoint Presentation
```javascript
// Step 3: Generate PowerPoint from student version
const presentationResponse = await fetch('http://localhost:5000/api/generate-presentation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_version: studentVersion,  // From Step 2
    n_slides: 10,
    language: 'Romanian',
    template: 'modern',
    tone: 'educational'
  })
});

const presentationData = await presentationResponse.json();
const presentation = presentationData.data.presentation;
const slides = presentationData.data.slides;

// Provide download link to teacher
const downloadLink = presentation.download_url;
const editLink = presentation.edit_url;

// Display presentation info
console.log(`Presentation created with ${presentation.n_slides} slides`);
console.log(`Credits used: ${presentation.credits_consumed}`);
console.log(`Download: ${downloadLink}`);
console.log(`Edit online: ${editLink}`);

// Display slide previews
slides.forEach((slide, index) => {
  console.log(`\nSlide ${index + 1}:`);
  console.log(`  Layout: ${slide.layout}`);
  console.log(`  Content:`, slide.content);
});
```

---

## Health Check Endpoint

**Endpoint:** `GET /api/health`

Simple endpoint to check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "message": "Romanian Education RAG API is running"
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/health
```

---

## Notes for Frontend Developers

1. **Subject field**: In the lecture generation endpoint, the `subject` field must match the metadata in the vector store. Typically this is lowercase (e.g., "biologie", "matematică", "fizică").

2. **HTML rendering**: Both `student_version` and `teacher_version` contain HTML. You can render them directly using `innerHTML` or use a sanitization library if you prefer additional security.

3. **Teacher notes styling**: The teacher version includes `<div class="teacher-note">` and `<span class="emphasis">` elements. You can style these in your CSS:
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

4. **Loading states**: 
   - Questions endpoint: ~5-10 seconds
   - Lecture endpoint: ~10-20 seconds
   - Presentation endpoint: ~30-60 seconds (Presenton API generates the slides)
   - Make sure to show loading indicators in your UI

5. **Answer format**: When a user selects "Altele" (Other) as an answer, they should be able to provide free-text input. Pass this custom text as the answer value.

6. **Presenton API Key**: The presentation endpoint requires a Presenton API key in the `.env` file. Get your key from [presenton.ai/account](https://presenton.ai/account). If the key is not configured, the endpoint will return a 503 error.

7. **Presentation files**: The `download_url` in the response is a direct link to the generated .pptx or .pdf file. You can either:
   - Open it in a new tab: `window.open(downloadUrl, '_blank')`
   - Create a download link: `<a href="${downloadUrl}" download>Download Presentation</a>`
   - Use the `edit_url` to allow teachers to edit the presentation online before downloading

8. **Slide data**: The `slides` array contains parsed content for each slide. You can use this to:
   - Show slide previews in your UI
   - Display slide count and structure before downloading
   - Create a custom slide editor if needed

9. **CORS**: The API has CORS enabled for all origins. In production, you may want to restrict this to your frontend domain.

---

## 4. Generate Podcast Endpoint

**Endpoint:** `POST /api/generate-podcast`

This endpoint generates an educational podcast from the lecture content using OpenAI GPT-4o to create a natural dialogue between two speakers (Ana - teacher and Mihai - student) and Async.ai text-to-speech API to convert the dialogue to audio. The result is a complete MP3 audio file with both voices.

### Request

**URL:** `http://localhost:5000/api/generate-podcast`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie...</p>",
  "teacher_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<div class=\"teacher-note\">[NOTĂ PROFESOR: Această lecție este concepută pentru clasa a 6-a...]</div>",
  "grade": 6,
  "subject": "Biologie",
  "target_duration": 300,
  "return_dialogue": true,
  "silence_between_turns": 500
}
```

**Field Descriptions:**
- `student_version` (string, required): The HTML content for students from `/api/generate-lecture`
- `teacher_version` (string, required): The HTML content for teachers from `/api/generate-lecture`
- `grade` (int, required): Grade level (1-12) for age-appropriate dialogue
- `subject` (string, required): Subject name for contextual dialogue
- `target_duration` (int, optional): Target podcast duration in seconds (default: 300, range: 60-1800)
- `return_dialogue` (boolean, optional): If true, returns JSON with audio and dialogue transcript. If false, returns audio file directly (default: true)
- `silence_between_turns` (int, optional): Milliseconds of silence between dialogue turns (default: 500)

### Response

**Success Response with Dialogue (200 OK):**
```json
{
  "success": true,
  "data": {
    "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAAGJgDU1NTU1NTU1NTU1NTU1NTU1NTU...",
    "audio_size_bytes": 245632,
    "dialogue": [
      {
        "speaker": "Ana",
        "text": "Bună, Mihai! Astăzi vom învăța despre celulă - unitatea structurală și funcțională a vieții. Ești gata să descoperim împreună ce este celula?"
      },
      {
        "speaker": "Mihai",
        "text": "Bună, Ana! Da, sunt foarte curios! Am auzit că toate viețuitoarele sunt făcute din celule, e adevărat?"
      },
      {
        "speaker": "Ana",
        "text": "Exact! Celula este cea mai mică unitate vie. Toate ființele vii, de la bacterii care au o singură celulă, până la oameni care au trilioane de celule, sunt alcătuite din aceste unități minuscule."
      }
    ],
    "metadata": {
      "grade": 6,
      "subject": "Biologie",
      "duration_target": 300,
      "turns_count": 10
    }
  }
}
```

For complete examples and more details, please refer to the updated API_EXAMPLES.md file.

