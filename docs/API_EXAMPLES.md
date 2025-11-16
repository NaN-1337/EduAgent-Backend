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

This endpoint generates an educational podcast from the lecture content using OpenAI GPT-4o to create a natural dialogue between two speakers (Ana - teacher and Bianca - student) and OpenAI text-to-speech API to convert the dialogue to audio. The result is a complete MP3 audio file uploaded to Firebase Storage.

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
  "teacher_id": "teacher_12345",
  "lecture_id": "lecture_67890",
  "target_duration": 300,
  "return_dialogue": true,
  "silence_between_turns": 500,
  "upload_to_firebase": true
}
```

**Field Descriptions:**
- `student_version` (string, required): The HTML content for students from `/api/generate-lecture`
- `teacher_version` (string, required): The HTML content for teachers from `/api/generate-lecture`
- `grade` (int, required): Grade level (1-12) for age-appropriate dialogue
- `subject` (string, required): Subject name for contextual dialogue
- `teacher_id` (string, required): Unique identifier for the teacher (used in Firebase Storage path)
- `lecture_id` (string, required): Unique identifier for the lecture (used in Firebase Storage path)
- `target_duration` (int, optional): Target podcast duration in seconds (default: 300, range: 60-1800)
- `return_dialogue` (boolean, optional): If true, includes dialogue transcript in response (default: true)
- `silence_between_turns` (int, optional): Milliseconds of silence between dialogue turns (default: 500)
- `upload_to_firebase` (boolean, optional): If true, uploads to Firebase Storage (default: true)

**Firebase Storage Path:**
The podcast will be stored at: `{teacher_id}/{grade}/{lecture_id}/podcast_{timestamp}.mp3`

Example: `teacher_12345/6/lecture_67890/podcast_20241116_143045.mp3`

### Response

**Success Response with Firebase Upload (200 OK):**
```json
{
  "success": true,
  "data": {
    "audio_base64": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAAGJgDU1NTU1NTU1NTU1NTU1NTU1NTU...",
    "audio_size_bytes": 2458624,
    "duration_seconds": 287.5,
    "dialogue": [
      {
        "speaker": "Ana",
        "text": "Bună, Bianca! Astăzi vom învăța despre celulă - unitatea structurală și funcțională a vieții. Ești gata să descoperim împreună ce este celula?"
      },
      {
        "speaker": "Bianca",
        "text": "Bună, Ana! Da, sunt foarte curios! Am auzit că toate viețuitoarele sunt făcute din celule, e adevărat?"
      },
      {
        "speaker": "Ana",
        "text": "Exact! Celula este cea mai mică unitate vie. Toate ființele vii, de la bacterii care au o singură celulă, până la oameni care au trilioane de celule, sunt alcătuite din aceste unități minuscule."
      }
    ],
    "firebase": {
      "path": "teacher_12345/6/lecture_67890/podcast_20241116_143045.mp3",
      "download_url": "https://storage.googleapis.com/your-bucket.appspot.com/teacher_12345/6/lecture_67890/podcast_20241116_143045.mp3?GoogleAccessId=...&Expires=...&Signature=...",
      "size_bytes": 2458624
    },
    "metadata": {
      "grade": 6,
      "subject": "Biologie",
      "teacher_id": "teacher_12345",
      "lecture_id": "lecture_67890",
      "duration_target": 300,
      "turns_count": 12
    }
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.audio_base64` (string): Base64-encoded MP3 audio data (if `return_dialogue=true`)
- `data.audio_size_bytes` (int): Size of the audio file in bytes
- `data.duration_seconds` (float): Actual duration of the generated podcast
- `data.dialogue` (array): Array of dialogue turns with speaker names and text (if `return_dialogue=true`)
- `data.firebase` (object): Firebase Storage information (if `upload_to_firebase=true`)
  - `path` (string): The path where the file is stored in Firebase Storage
  - `download_url` (string): Signed URL for downloading the file (valid for 7 days)
  - `size_bytes` (int): Size of the uploaded file
- `data.metadata` (object): Additional information about the podcast generation

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: teacher_id and lecture_id are required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: Firebase Storage is not available. Please configure Firebase credentials."
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "error": "Podcast service is not available: ffmpeg/ffprobe not found"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "student_version": "<h1>Celula</h1><p>Celula este cea mai mică unitate vie...</p>",
    "teacher_version": "<h1>Celula</h1><div class=\"teacher-note\">[NOTĂ PROFESOR...]</div>",
    "grade": 6,
    "subject": "Biologie",
    "teacher_id": "teacher_12345",
    "lecture_id": "lecture_67890",
    "target_duration": 180,
    "return_dialogue": true,
    "upload_to_firebase": true
  }'
```

### Python Example
```python
import requests
import json

# Generate podcast with Firebase upload
response = requests.post(
    'http://localhost:5000/api/generate-podcast',
    json={
        'student_version': student_html,  # From /api/generate-lecture
        'teacher_version': teacher_html,  # From /api/generate-lecture
        'grade': 6,
        'subject': 'Biologie',
        'teacher_id': 'teacher_12345',
        'lecture_id': 'lecture_67890',
        'target_duration': 300,
        'return_dialogue': True,
        'upload_to_firebase': True
    }
)

if response.status_code == 200:
    data = response.json()
    
    # Get Firebase download URL
    firebase_url = data['data']['firebase']['download_url']
    print(f"Podcast uploaded to: {firebase_url}")
    
    # Get dialogue transcript
    dialogue = data['data']['dialogue']
    for turn in dialogue:
        print(f"{turn['speaker']}: {turn['text']}")
    
    # Optionally save audio locally from base64
    import base64
    audio_bytes = base64.b64decode(data['data']['audio_base64'])
    with open('podcast.mp3', 'wb') as f:
        f.write(audio_bytes)
else:
    print(f"Error: {response.json()['error']}")
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-podcast', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    student_version: studentVersionHTML,  // From previous endpoint
    teacher_version: teacherVersionHTML,  // From previous endpoint
    grade: 6,
    subject: 'Biologie',
    teacher_id: 'teacher_12345',
    lecture_id: 'lecture_67890',
    target_duration: 300,
    return_dialogue: true,
    upload_to_firebase: true
  })
})
  .then(response => response.json())
  .then(data => {
    const firebaseUrl = data.data.firebase.download_url;
    const dialogue = data.data.dialogue;
    const duration = data.data.duration_seconds;
    
    console.log(`Podcast generated: ${duration}s`);
    console.log(`Download from: ${firebaseUrl}`);
    
    // Display dialogue transcript
    dialogue.forEach(turn => {
      console.log(`${turn.speaker}: ${turn.text}`);
    });
    
    // Play audio in browser
    const audio = new Audio(`data:audio/mpeg;base64,${data.data.audio_base64}`);
    audio.play();
  })
  .catch(error => console.error('Error:', error));
```

**Important Notes:**

1. **Firebase Storage**: Requires Firebase credentials to be configured in `.env`:
   - `FIREBASE_SERVICE_ACCOUNT_PATH`: Path to service account JSON file
   - `FIREBASE_STORAGE_BUCKET`: Your Firebase Storage bucket name

2. **Storage Structure**: Podcasts are organized by teacher, grade, and lecture:
   ```
   teacher_12345/
   ├── 6/
   │   ├── lecture_67890/
   │   │   ├── podcast_20241116_143045.mp3
   │   │   └── podcast_20241116_150230.mp3
   │   └── lecture_67891/
   │       └── podcast_20241116_144512.mp3
   └── 7/
       └── lecture_67892/
           └── podcast_20241116_145623.mp3
   ```

3. **Download URLs**: The signed URLs are valid for 7 days. After expiration, you can generate new URLs using Firebase Admin SDK or Firebase Console.

4. **Local Storage**: By default, podcasts are NOT saved locally. If `upload_to_firebase=false`, the endpoint will return audio data but won't persist it anywhere.

5. **Audio Format**: Generated podcasts are in MP3 format with stereo audio at 44.1kHz.

6. **Processing Time**: Podcast generation typically takes 30-90 seconds depending on target duration:
   - 2-3 minutes podcast: ~30-45 seconds
   - 5 minutes podcast: ~60-90 seconds
   - Show loading indicator in your UI

7. **Voices**: Uses OpenAI TTS with Romanian-capable voices:
   - **Ana** (female): "nova" voice - warm, clear
   - **Bianca** (male): "onyx" voice - deep, authoritative

8. **Error Handling**: The endpoint includes graceful error handling. If Firebase is not configured but `upload_to_firebase=true`, it will return a clear error message rather than failing silently.

---

## 5. Generate Homework Questions Endpoint

**Endpoint:** `POST /api/generate-homework-questions`

This endpoint generates clarifying questions that help gather information for creating appropriate homework exercises based on lesson content.

### Request

**URL:** `http://localhost:5000/api/generate-homework-questions`

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
  "lesson_content": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate structurală și funcțională a vieții...</p>",
  "num_exercises": 5,
  "subject": "Biologie",
  "grade": 6
}
```

**Field Descriptions:**
- `lesson_content` (string, required): The lesson content in HTML or plain text format
- `num_exercises` (int, required): Number of homework exercises to generate (1-20)
- `subject` (string, required): Subject name (e.g., "Matematică", "Biologie")
- `grade` (int, required): Grade level (1-12)

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": 1,
        "question": "Ce nivel de dificultate ar trebui să aibă exercițiile?",
        "type": "single-choice",
        "options": [
          "Ușor - consolidare concepte de bază",
          "Mediu - aplicare și înțelegere",
          "Dificil - analiză și sinteză",
          "Mixt - combinație de niveluri",
          "Altele"
        ]
      },
      {
        "id": 2,
        "question": "Ce tipuri de exerciții preferați?",
        "type": "multiple-choice",
        "options": [
          "Întrebări cu alegere multiplă",
          "Întrebări cu răspuns scurt",
          "Probleme de rezolvat",
          "Exerciții de aplicare practică",
          "Sarcini creative/proiecte",
          "Altele"
        ]
      },
      {
        "id": 3,
        "question": "Cât timp ar trebui să aloce elevii pentru această temă?",
        "type": "single-choice",
        "options": [
          "15-20 minute",
          "30-40 minute",
          "50-60 minute",
          "Peste o oră",
          "Altele"
        ]
      },
      {
        "id": 4,
        "question": "Ar trebui să includem indicii sau ghidaj pentru exerciții?",
        "type": "yes-no",
        "options": [
          "Da",
          "Nu"
        ]
      }
    ]
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: lesson_content, num_exercises, subject, and grade are required"
}
```

---

## 6. Generate Homework Endpoint

**Endpoint:** `POST /api/generate-homework`

This endpoint generates homework exercises based on lesson content using RAG (Retrieval-Augmented Generation) with curriculum context.

### Request

**URL:** `http://localhost:5000/api/generate-homework`

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
  "lesson_content": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate structurală și funcțională a vieții. Toate organismele vii sunt formate din una sau mai multe celule...</p>\n\n<h2>Structura celulei</h2>\n<p>Celula are mai multe părți importante: membrana celulară, citoplasma și nucleul...</p>",
  "num_exercises": 5,
  "subject": "biologie",
  "grade": 6,
  "questions": [
    {
      "id": 1,
      "question": "Ce nivel de dificultate ar trebui să aibă exercițiile?",
      "type": "single-choice",
      "options": ["Ușor", "Mediu", "Dificil", "Mixt", "Altele"]
    },
    {
      "id": 2,
      "question": "Ce tipuri de exerciții preferați?",
      "type": "multiple-choice",
      "options": ["Întrebări cu alegere multiplă", "Întrebări cu răspuns scurt", "Probleme de rezolvat", "Altele"]
    }
  ],
  "answers": {
    "1": "Mediu - aplicare și înțelegere",
    "2": "Combinație de tipuri"
  }
}
```

**Field Descriptions:**
- `lesson_content` (string, required): The lesson content in HTML or plain text format
- `num_exercises` (int, required): Number of homework exercises to generate (1-20)
- `subject` (string, required): Subject name (lowercase, e.g., "biologie", "matematică")
- `grade` (int, required): Grade level (1-12)
- `questions` (array, required): Array of question objects from homework questions endpoint
- `answers` (object, required): Dictionary mapping question IDs to selected answers

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "homework": "<h1>Temă pentru acasă - Biologie</h1>\n\n<h2>Celula - unitatea structurală și funcțională a vieții</h2>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 1</span>\n    <span class=\"points\">(10 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Alege varianta corectă. Care dintre următoarele afirmații despre celulă este adevărată?</p>\n    <ul>\n      <li>a) Celula este cea mai mare unitate structurală a vieții</li>\n      <li>b) Celula este cea mai mică unitate funcțională a vieții</li>\n      <li>c) Toate celulele au aceeași formă</li>\n      <li>d) Celulele nu pot supraviețui independent</li>\n    </ul>\n  </div>\n</div>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 2</span>\n    <span class=\"points\">(15 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Numește cele trei părți principale ale unei celule și descrie pe scurt rolul fiecăreia.</p>\n  </div>\n</div>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 3</span>\n    <span class=\"points\">(15 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Compară celula animală cu celula vegetală. Menționează două asemănări și două deosebiri.</p>\n  </div>\n</div>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 4</span>\n    <span class=\"points\">(20 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Explică de ce celula este considerată \"unitatea structurală și funcțională a vieții\". Folosește exemple pentru a-ți susține răspunsul.</p>\n  </div>\n</div>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 5</span>\n    <span class=\"points\">(20 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Desenează schema unei celule (animală sau vegetală, la alegere) și etichetează cel puțin 5 componente ale acesteia. Adaugă o scurtă descriere a funcției fiecărei componente desenate.</p>\n  </div>\n</div>\n\n<p><strong>Total puncte: 80</strong></p>"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: lesson_content, num_exercises, subject, grade, questions, and answers are required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: Vector store not found"
}
```

### Usage Flow

The homework generation follows a two-step workflow:

1. **Step 1:** Call `/api/generate-homework-questions` to get clarifying questions
   - Provide lesson content, number of exercises, subject, and grade
   - Receive questions about difficulty level, exercise types, time allocation, etc.

2. **Step 2:** Call `/api/generate-homework` to generate exercises
   - Provide all parameters from Step 1
   - Add the questions and answers from Step 1
   - Receive complete homework with various exercise types in HTML format

### HTML Structure

The homework HTML includes styled elements:
- `<h1>` - Main title
- `<h2>` - Section headers
- `<div class="exercise">` - Exercise container
- `<div class="exercise-header">` - Exercise number and points
- `<div class="exercise-content">` - Exercise text and questions
- `<span class="exercise-number">` - Exercise number
- `<span class="points">` - Point value
- `<div class="hint">` - Optional hints (if requested)

---

## 7. Chat Endpoint

**Endpoint:** `POST /api/chat`

This endpoint provides an educational chatbot assistant that adapts its tone and communication style based on user role (student or individual). Maintains session-based conversation history.

### Request

**URL:** `http://localhost:5000/api/chat`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body for NEW session (Student):**
```json
{
  "lesson_content": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate structurală și funcțională a vieții...</p>",
  "user_prompt": "Ce este citoplasma și la ce servește?",
  "subject": "Biologie",
  "user_role": "student",
  "grade": 6
}
```

**Body for NEW session (Individual):**
```json
{
  "lesson_content": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate structurală și funcțională a vieții...</p>",
  "user_prompt": "Care sunt diferențele principale între celula procariotă și eucariotă?",
  "subject": "Biologie",
  "user_role": "individual"
}
```

**Body for EXISTING session (follow-up):**
```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_prompt": "Poți să-mi dai un exemplu mai simplu?"
}
```

**Field Descriptions:**
- `lesson_content` (string, required for new session): The lesson content in HTML format from `/api/generate-lecture`
- `user_prompt` (string, required): The user's question or message
- `subject` (string, required for new session): Subject name (e.g., "Biologie", "Matematică")
- `user_role` (string, required for new session): Either "student" or "individual"
- `grade` (int, required if user_role is "student"): Grade level (1-12)
- `session_id` (string, optional): Session ID from previous chat. If provided, continues existing conversation

### Response

**Success Response - New Session (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "response": "Bună! Citoplasma este un fel de 'supă' specială care umple celula. Gândește-te la celulă ca la un balon umplut cu apă – citoplasma este acea apă, dar mult mai specială! \n\nÎn citoplasma plutesc toate organitele celulei, ca niște jucării într-o piscină. Ea le ține pe toate la locul lor și le ajută să lucreze împreună.\n\nCitoplasma mai are și un rol foarte important: transportă substanțele nutritive (ca mâncarea pentru celulă) și ajută la eliminarea deșeurilor (ca un sistem de curățenie).\n\nAi mai vrea să știi ceva despre părțile celulei? 😊",
    "user_role": "student",
    "grade": 6,
    "message_count": 2
  }
}
```

**Success Response - Continuing Session (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "response": "Sigur! Hai să folosim un exemplu simplu pe care îl cunoști:\n\nGândește-te că celula este ca o școală:\n- Membrana celulară este ca poarta școlii - controlează cine intră și cine iese\n- Citoplasma este ca holurile și sălile de clasă - acolo se întâmplă totul\n- Nucleul este ca directorul școlii - el dă ordinele și se asigură că totul funcționează bine\n\nȘi cum în școală ai profesori, bibliotecă, cantină - tot așa și în citoplasmă sunt organite care au fiecare treaba lor! Cool, nu? 🏫",
    "user_role": "student",
    "grade": 6,
    "message_count": 4
  }
}
```

**Success Response - Individual User (200 OK):**
```json
{
  "success": true,
  "data": {
    "session_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
    "response": "Diferențele principale între celulele procariote și eucariote sunt:\n\n**Celule Procariote:**\n- Nu au nucleu delimitat de membrană - materialul genetic este liber în citoplasmă (în regiunea numită nucleoid)\n- Nu au organite învelite în membrane\n- Ribozomi mai mici (70S)\n- ADN circular\n- Exemple: bacterii, arhee\n\n**Celule Eucariote:**\n- Au nucleu delimitat de membrană nucleară\n- Conțin organite specializate (mitocondrii, aparat Golgi, reticulul endoplasmatic, etc.)\n- Ribozomi mai mari (80S)\n- ADN liniar organizat în cromozomi\n- Exemple: celule animale, vegetale, fungi, protiste\n\nAceastă diferențiere fundamentală reflectă evoluția complexității celulare și specializarea funcțiilor. Celulele eucariote permit o organizare mult mai complexă datorită compartimentării proceselor metabolice în organite distincte.\n\nDoriți să aprofundăm vreun aspect specific al acestor diferențe?",
    "user_role": "individual",
    "grade": null,
    "message_count": 2
  }
}
```

**Error Response (400 Bad Request) - Missing parameters:**
```json
{
  "error": "Missing required parameter: user_prompt is required"
}
```

**Error Response (404 Not Found) - Session expired:**
```json
{
  "error": "Session not found or expired. Please create a new session."
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: [error details]"
}
```

### Key Features

**Role-Based Adaptation:**
- **Student (Grades 1-4)**: Very simple, playful language with emojis, short sentences, storytelling
- **Student (Grades 5-8)**: Friendly, conversational, examples from their interests, balanced playfulness
- **Student (Grades 9-12)**: Mature, respectful, academic tone, real-world applications, university prep
- **Individual**: Professional, comprehensive, detailed explanations for adult learners

**Session Management:**
- Sessions are temporary and stored in-memory (not persisted to database)
- Sessions expire after 1 hour of inactivity
- Each session maintains its own conversation history
- Automatic cleanup of expired sessions

**Web Search Capability:**
- Uses GPT-4o model with web search capabilities
- Can provide current information and additional examples
- Verifies information from credible sources

### Usage Flow

**Flow for New Session:**
1. Frontend calls `/api/generate-lecture` to get lesson content
2. User starts chat with lesson content, first prompt, role, and grade (if student)
3. Backend creates new session, generates response
4. Frontend stores `session_id` for subsequent messages

**Flow for Continuing Session:**
1. User sends another message with existing `session_id` and new prompt
2. Backend retrieves session, maintains context from conversation history
3. Chatbot generates contextual response
4. Session automatically updated with new messages

### Example JavaScript Integration

```javascript
// Start new chat session
async function startChat(lessonContent, subject, userRole, grade = null) {
  const payload = {
    lesson_content: lessonContent,
    user_prompt: "Bună! Poți să mă ajuți să înțeleg această lecție?",
    subject: subject,
    user_role: userRole
  };
  
  if (userRole === "student") {
    payload.grade = grade;
  }
  
  const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  const data = await response.json();
  
  // Store session_id for future messages
  sessionStorage.setItem('chat_session_id', data.data.session_id);
  
  return data.data;
}

// Continue existing chat
async function sendMessage(message) {
  const sessionId = sessionStorage.getItem('chat_session_id');
  
  const response = await fetch('http://localhost:5000/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      user_prompt: message
    })
  });
  
  const data = await response.json();
  
  if (response.status === 404) {
    // Session expired, need to create new session
    console.error('Session expired');
    return null;
  }
  
  return data.data;
}

// Example usage
const studentData = await startChat(lessonHTML, "Biologie", "student", 6);
console.log("Chatbot:", studentData.response);

const followUp = await sendMessage("Poți să-mi dai un exemplu?");
console.log("Chatbot:", followUp.response);
```

---

## 8. Generate Quiz Endpoint

**Endpoint:** `POST /api/generate-quiz`

This endpoint generates a single-choice quiz based on lecture content. The AI creates questions that can only be answered using information explicitly stated in the provided content, ensuring alignment with what was taught.

### Request

**URL:** `http://localhost:5000/api/generate-quiz`

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
  "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie a organismelor...</p>",
  "num_questions": 10
}
```

**Field Descriptions:**
- `student_version` (string, required): The HTML content from the student version of the lecture (from `/api/generate-lecture`)
- `num_questions` (int, optional): Number of questions to generate (default: 10, range: 1-50)

**Important**: The quiz questions are generated **only** from information in the `student_version` content. This ensures students can answer all questions based on what they learned.

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "questions": [
      {
        "id": "q1",
        "text": "Care este cea mai mică unitate vie a organismelor?",
        "options": [
          {
            "id": "a",
            "text": "Celula"
          },
          {
            "id": "b",
            "text": "Țesutul"
          },
          {
            "id": "c",
            "text": "Organul"
          },
          {
            "id": "d",
            "text": "Sistemul"
          }
        ],
        "correctAnswerId": "a"
      },
      {
        "id": "q2",
        "text": "Ce componentă celulară conține materialul genetic (ADN)?",
        "options": [
          {
            "id": "a",
            "text": "Membrana celulară"
          },
          {
            "id": "b",
            "text": "Citoplasma"
          },
          {
            "id": "c",
            "text": "Nucleul"
          },
          {
            "id": "d",
            "text": "Peretele celular"
          }
        ],
        "correctAnswerId": "c"
      },
      {
        "id": "q3",
        "text": "Ce diferență majoră există între celula animală și cea vegetală?",
        "options": [
          {
            "id": "a",
            "text": "Celula vegetală nu are nucleu"
          },
          {
            "id": "b",
            "text": "Celula animală nu are citoplasma"
          },
          {
            "id": "c",
            "text": "Celula vegetală are perete celular rigid"
          },
          {
            "id": "d",
            "text": "Celula animală este mai mare"
          }
        ],
        "correctAnswerId": "c"
      }
    ]
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.questions` (array): Array of quiz questions
  - `id` (string): Unique identifier for the question (e.g., "q1", "q2")
  - `text` (string): The question text in Romanian
  - `options` (array): Array of 4 answer options
    - `id` (string): Option identifier (a, b, c, d)
    - `text` (string): Option text
  - `correctAnswerId` (string): ID of the correct answer option

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameter: student_version"
}
```

```json
{
  "error": "num_questions must be between 1 and 50"
}
```

```json
{
  "error": "Student version content is too short to generate meaningful questions"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Internal server error: Failed to parse quiz from AI response"
}
```

**Error Response (503 Service Unavailable):**
```json
{
  "error": "Quiz service is not available"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-quiz \
  -H "Content-Type: application/json" \
  -d '{
    "student_version": "<h1>Celula</h1><p>Celula este cea mai mică unitate vie...</p>",
    "num_questions": 5
  }'
```

### Python Example
```python
import requests

# Generate quiz from lecture content
response = requests.post(
    'http://localhost:5000/api/generate-quiz',
    json={
        'student_version': student_html,  # From /api/generate-lecture
        'num_questions': 10
    }
)

if response.status_code == 200:
    data = response.json()
    questions = data['data']['questions']
    
    print(f"Generated {len(questions)} questions:")
    for q in questions:
        print(f"\n{q['text']}")
        for opt in q['options']:
            marker = "✓" if opt['id'] == q['correctAnswerId'] else " "
            print(f"  {marker} {opt['id']}) {opt['text']}")
else:
    print(f"Error: {response.json()['error']}")
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-quiz', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    student_version: studentVersionHTML,  // From /api/generate-lecture
    num_questions: 10
  })
})
  .then(response => response.json())
  .then(data => {
    const questions = data.data.questions;
    
    // Display quiz in your UI
    questions.forEach((question, index) => {
      console.log(`\nQuestion ${index + 1}: ${question.text}`);
      
      question.options.forEach(option => {
        const isCorrect = option.id === question.correctAnswerId;
        console.log(`  ${option.id}) ${option.text} ${isCorrect ? '✓' : ''}`);
      });
    });
  })
  .catch(error => console.error('Error:', error));
```

### Integration Example: Complete Workflow
```javascript
// Step 1: Generate lecture
const lectureResponse = await fetch('/api/generate-lecture', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Celula - unitatea structurală și funcțională a vieții',
    subject: 'biologie',
    grade: 6,
    questions: [...],  // From /api/generate-questions
    answers: {...}
  })
});

const lectureData = await lectureResponse.json();
const studentVersion = lectureData.data.student_version;

// Step 2: Generate quiz from lecture content
const quizResponse = await fetch('/api/generate-quiz', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_version: studentVersion,
    num_questions: 10
  })
});

const quizData = await quizResponse.json();
const quiz = quizData.data.questions;

// Step 3: Save quiz to Firestore
await db.collection('quizzes').add({
  lectureId: 'lecture_xyz789',
  teacherId: currentTeacherId,
  title: 'Test: Celula - Structura și funcțiile',
  subject: 'Biologie',
  grade: 6,
  totalQuestions: quiz.length,
  questions: quiz,
  createdAt: firebase.firestore.FieldValue.serverTimestamp()
});

console.log('Quiz generated and saved successfully!');
```

**Important Notes:**

1. **Content-Based Questions**: The AI only generates questions based on information explicitly stated in `student_version`. This ensures quiz alignment with the lecture content.

2. **Coverage**: The service attempts to distribute questions across the entire lecture content to test comprehensive understanding.

3. **Question Quality**: Questions vary in difficulty, including both basic recall and deeper understanding questions.

4. **Answer Options**: Wrong answers are plausible but clearly incorrect based on the content, requiring careful reading to distinguish.

5. **Processing Time**: Quiz generation typically takes 5-15 seconds depending on content length and number of questions.

6. **Content Length**: The content must be at least 100 characters long. For best results, use complete lecture content with multiple sections.

7. **Question Limits**: You can request 1-50 questions. For shorter lectures (< 500 words), requesting fewer questions (5-10) produces better quality.

8. **Validation**: The service validates the quiz structure to ensure all questions have exactly 4 options and valid correct answer IDs.

---

## 8. Parse Submission Endpoint

**Endpoint:** `POST /api/parse-submission`

This endpoint downloads a PDF or image homework submission from a URL and uses GPT-4o Vision API to extract handwritten text. PDFs are converted to images and processed page by page. Image files (JPEG, PNG) are processed directly.

### Request

**URL:** `http://localhost:5000/api/parse-submission`

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
  "submission_url": "https://storage.googleapis.com/your-bucket/submissions/student_homework.pdf"
}
```

**Alternative (Image File):**
```json
{
  "submission_url": "https://storage.googleapis.com/your-bucket/submissions/homework_photo.jpg"
}
```

**Field Descriptions:**
- `submission_url` (string, required): URL of the PDF or image file (JPEG, PNG) containing the student's handwritten homework submission

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "parsed_text": "=== PAGE 1 ===\n\nExercițiul 1\nCelula este cea mai mică unitate structurală și funcțională a vieții. Toate organismele sunt formate din celule.\n\n=== PAGE 2 ===\n\nExercițiul 2\nPărțile principale ale celulei sunt:\n1. Membrana celulară - protejează celula\n2. Citoplasma - substanță gelatinoasă\n3. Nucleul - conține ADN\n\nExercițiul 3\nCelula animală nu are perete celular, dar celula vegetală are perete celular rigid...",
    "page_count": 2,
    "pages": [
      "=== PAGE 1 ===\n\nExercițiul 1\nCelula este cea mai mică unitate structurală și funcțională a vieții...",
      "=== PAGE 2 ===\n\nExercițiul 2\nPărțile principale ale celulei sunt..."
    ]
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.parsed_text` (string): Complete transcribed text from all pages combined
- `data.page_count` (int): Number of pages processed
- `data.pages` (array): Array of transcribed text for each individual page

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameter: submission_url is required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Failed to parse PDF: URL does not point to a supported file (PDF, JPEG, PNG)"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/parse-submission \
  -H "Content-Type: application/json" \
  -d '{
    "submission_url": "https://storage.googleapis.com/your-bucket/submissions/homework.pdf"
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/parse-submission', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    submission_url: 'https://storage.googleapis.com/your-bucket/submissions/homework.pdf'
  })
})
  .then(response => response.json())
  .then(data => {
    const parsedText = data.data.parsed_text;
    const pageCount = data.data.page_count;
    
    console.log(`Parsed ${pageCount} pages`);
    console.log('Extracted text:', parsedText);
  })
  .catch(error => console.error('Error:', error));
```

**Important Notes:**

1. **File Requirements**: The URL must point to a valid PDF or image file (JPEG, PNG). The service checks the content type and file extension.

2. **Image File Support**: You can submit:
   - PDF files (multi-page support)
   - JPEG images (.jpg, .jpeg)
   - PNG images (.png)

3. **Handwriting Recognition**: Uses GPT-4o Vision with high detail mode for accurate transcription of handwritten text.

4. **Processing Time**: 
   - Images (JPEG/PNG): ~5-10 seconds per image
   - PDF files: ~5-10 seconds per page
   - A 3-page PDF takes approximately 15-30 seconds

5. **Page Limit**: Maximum 20 pages per PDF to prevent excessive processing time and API costs. Single images are always processed.

6. **Image Quality**: PDFs are converted to images at 300 DPI for optimal OCR accuracy.

7. **Text Formatting**: Mathematical notation is converted to text format (e.g., "x^2", "√4"). Diagrams are described as [DIAGRAM: description].

8. **Illegible Text**: If handwriting is unclear, the service marks it as [ILLEGIBLE] with a best guess [maybe: ...].

---

## 9. Grade Homework Endpoint

**Endpoint:** `POST /api/grade-homework`

This endpoint automatically grades a homework submission by comparing the student's parsed solutions with the original homework assignment. It provides exercise-by-exercise grading with partial credit support (multiples of 0.25) and generates detailed feedback.

### Request

**URL:** `http://localhost:5000/api/grade-homework`

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
  "homework_html": "<h1>Temă pentru acasă - Biologie</h1>\n\n<div class=\"exercise\">\n  <div class=\"exercise-header\">\n    <span class=\"exercise-number\">Exercițiul 1</span>\n    <span class=\"points\">(10 puncte)</span>\n  </div>\n  <div class=\"exercise-content\">\n    <p>Explică ce este celula și de ce este considerată unitatea structurală a vieții.</p>\n  </div>\n</div>...",
  "parsed_submission": "=== PAGE 1 ===\n\nExercițiul 1\nCelula este cea mai mică unitate vie. Este unitatea structurală pentru că toate organismele sunt făcute din celule...",
  "subject": "Biologie",
  "grade": 6
}
```

**Field Descriptions:**
- `homework_html` (string, required): The original homework assignment in HTML format (from `/api/generate-homework`)
- `parsed_submission` (string, required): The parsed text from the student's PDF submission (from `/api/parse-submission`)
- `subject` (string, optional): Subject name for context
- `grade` (int, optional): Grade level for context

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "total_points_earned": 37.5,
    "total_points_possible": 50,
    "final_grade_percentage": 75.0,
    "exercises": [
      {
        "exercise_number": 1,
        "exercise_content": "Explică ce este celula și de ce este considerată unitatea structurală a vieții.",
        "student_solution": "Celula este cea mai mică unitate vie. Este unitatea structurală pentru că toate organismele sunt făcute din celule.",
        "points_earned": 8.5,
        "max_points": 10.0,
        "percentage": 85.0,
        "feedback": "Foarte bine! Ai înțeles conceptul fundamental că celula este cea mai mică unitate vie și ai menționat corect că toate organismele sunt formate din celule. Pentru punctaj maxim, ar fi fost ideal să menționezi și aspectul funcțional - că toate procesele vitale au loc la nivel celular. Continuă așa!",
        "is_correct": false,
        "is_partial": true
      },
      {
        "exercise_number": 2,
        "exercise_content": "Numește cele trei părți principale ale unei celule și descrie pe scurt rolul fiecăreia.",
        "student_solution": "1. Membrana celulară - protejează celula și controlează ce intră și iese\n2. Citoplasma - substanță gelatinoasă unde se întâmplă procesele\n3. Nucleul - conține ADN și controlează celula",
        "points_earned": 15.0,
        "max_points": 15.0,
        "percentage": 100.0,
        "feedback": "Excelent! Ai identificat corect toate cele trei părți principale ale celulei și ai oferit descrieri precise și complete pentru fiecare. Răspunsul tău demonstrează o înțelegere foarte bună a structurii celulare. Bravo!",
        "is_correct": true,
        "is_partial": false
      },
      {
        "exercise_number": 3,
        "exercise_content": "Compară celula animală cu celula vegetală. Menționează două asemănări și două deosebiri.",
        "student_solution": "Asemănări: amândouă au membrană, citoplasmă și nucleu.\nDeosebiri: celula vegetală are perete celular și cloroplaste, celula animală nu are.",
        "points_earned": 14.0,
        "max_points": 15.0,
        "percentage": 93.0,
        "feedback": "Foarte bine! Ai identificat corect asemănările și deosebirile principale între celula animală și vegetală. Răspunsul este aproape complet. Pentru punctaj maxim, ai fi putut menționa că ai găsit o asemănare (toate trei componentele de bază) și două deosebiri clare (perete celular și cloroplaste). Totuși, conținutul este corect și demonstrează înțelegere solidă!",
        "is_correct": false,
        "is_partial": true
      }
    ],
    "overall_feedback": "**Nota finală: 37.5/50 puncte (75.0%)**\n\n**Sumar:**\n- Exerciții corecte: 1/3\n- Exerciții parțial corecte: 2/3\n\n**Evaluare generală:**\nFoarte bine! Ai o înțelegere solidă, cu mici aspecte de îmbunătățit.",
    "subject": "Biologie",
    "grade_level": 6
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.total_points_earned` (float): Total points earned across all exercises
- `data.total_points_possible` (float): Total points possible for the homework
- `data.final_grade_percentage` (float): Overall percentage score
- `data.exercises` (array): Array of graded exercise results
  - `exercise_number` (int): Exercise number
  - `exercise_content` (string): The original exercise question
  - `student_solution` (string): The parsed student solution
  - `points_earned` (float): Points earned (rounded to nearest 0.25)
  - `max_points` (float): Maximum points for the exercise
  - `percentage` (float): Percentage score for this exercise
  - `feedback` (string): Detailed feedback in Romanian
  - `is_correct` (boolean): True if ≥95% correct
  - `is_partial` (boolean): True if partially correct (>0% and <95%)
- `data.overall_feedback` (string): Overall performance summary and recommendations
- `data.subject` (string): Subject name
- `data.grade_level` (int): Grade level

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameters: homework_html and parsed_submission are required"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Nu s-au putut extrage exercițiile din tema de casă."
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/grade-homework \
  -H "Content-Type: application/json" \
  -d '{
    "homework_html": "<h1>Temă pentru acasă</h1>...",
    "parsed_submission": "Exercițiul 1...",
    "subject": "Biologie",
    "grade": 6
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/grade-homework', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    homework_html: homeworkHTML,  // From /api/generate-homework
    parsed_submission: parsedText,  // From /api/parse-submission
    subject: 'Biologie',
    grade: 6
  })
})
  .then(response => response.json())
  .then(data => {
    const totalScore = data.data.total_points_earned;
    const totalPossible = data.data.total_points_possible;
    const percentage = data.data.final_grade_percentage;
    const exercises = data.data.exercises;
    
    console.log(`Grade: ${totalScore}/${totalPossible} (${percentage}%)`);
    
    // Display exercise-by-exercise results
    exercises.forEach(ex => {
      console.log(`Exercise ${ex.exercise_number}: ${ex.points_earned}/${ex.max_points}`);
      console.log(`Feedback: ${ex.feedback}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

---

## Complete Homework Grading Workflow

Here's the complete flow for homework generation, submission, and grading:

### Step 1: Generate Homework
```javascript
// Generate homework assignment
const homeworkResponse = await fetch('http://localhost:5000/api/generate-homework', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    lesson_content: lessonHTML,
    num_exercises: 5,
    subject: 'biologie',
    grade: 6,
    questions: questions,
    answers: answers
  })
});

const homeworkData = await homeworkResponse.json();
const homeworkHTML = homeworkData.data.homework;

// Display homework to student
document.getElementById('homework').innerHTML = homeworkHTML;
```

### Step 2: Student Completes and Uploads PDF
```javascript
// Student uploads their handwritten homework as PDF
// Upload to your storage (Firebase, AWS S3, etc.)
const submissionURL = await uploadPDFToStorage(pdfFile);
// Returns: "https://storage.googleapis.com/.../homework_submission.pdf"
```

### Step 3: Parse the Submission
```javascript
// Parse the handwritten PDF submission
const parseResponse = await fetch('http://localhost:5000/api/parse-submission', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    submission_url: submissionURL
  })
});

const parseData = await parseResponse.json();
const parsedText = parseData.data.parsed_text;

console.log('Parsed submission:', parsedText);
```

### Step 4: Grade the Submission
```javascript
// Grade the homework
const gradeResponse = await fetch('http://localhost:5000/api/grade-homework', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    homework_html: homeworkHTML,  // From Step 1
    parsed_submission: parsedText,  // From Step 3
    subject: 'Biologie',
    grade: 6
  })
});

const gradeData = await gradeResponse.json();

// Display results
const score = gradeData.data.total_points_earned;
const total = gradeData.data.total_points_possible;
const percentage = gradeData.data.final_grade_percentage;

console.log(`Final Grade: ${score}/${total} (${percentage}%)`);
console.log('Overall Feedback:', gradeData.data.overall_feedback);

// Show exercise-by-exercise results
gradeData.data.exercises.forEach(exercise => {
  console.log(`\nExercise ${exercise.exercise_number}:`);
  console.log(`Score: ${exercise.points_earned}/${exercise.max_points}`);
  console.log(`Feedback: ${exercise.feedback}`);
});
```

**Important Notes:**

1. **Partial Credit**: Scores are automatically rounded to the nearest 0.25 (quarter points). For example:
   - 75% of 10 points = 7.5 points
   - 33% of 5 points = 1.5 → rounds to 1.5 points
   - 40% of 5 points = 2.0 points

2. **Grading Criteria**: The AI evaluates with strict attention to detail:
   - **Correct methodology and approach**: up to 50% of points
   - **Correct intermediate steps**: up to 25% of points
   - **Correct final answer**: up to 25% of points
   - **Maximum 75% if final answer is wrong** (even with correct method)
   - For math problems, arithmetic accuracy is verified independently

3. **Arithmetic Verification**: For mathematical exercises, a second AI verification step checks:
   - If all calculations are arithmetically correct
   - If the final answer satisfies the equation/problem
   - Any calculation errors are identified and noted in feedback

4. **Processing Time**: 
   - Parsing: ~5-10 seconds per PDF page/image
   - Grading: ~5-8 seconds per exercise (includes verification)
   - Total for 5-exercise homework: ~30-50 seconds

5. **Feedback Quality**: All feedback is provided in Romanian and is:
   - Constructive and educational
   - Specific to what the student did right/wrong
   - Includes arithmetic error notifications when detected
   - Includes suggestions for improvement

6. **Exercise Detection**: The grading service automatically detects exercise boundaries in the parsed submission by looking for markers like "Exercițiul 1", "Ex. 2", etc.

7. **Missing Solutions**: If an exercise solution is not found in the parsed submission, it's marked as [LIPSEȘTE SOLUȚIA] and receives 0 points.

8. **HTML Format**: The homework_html must be in the format generated by `/api/generate-homework` with proper exercise div structure and point values.

---

## 10. Generate Flashcards Endpoint

**Endpoint:** `POST /api/generate-flashcards`

This endpoint generates educational flashcards from lesson content using GPT-4o. Flashcards are created as question-answer pairs that help students review and memorize key concepts from the lesson.

### Request

**URL:** `http://localhost:5000/api/generate-flashcards`

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
  "student_version": "<h1>Celula - unitatea structurală și funcțională a vieții</h1>\n\n<h2>Introducere</h2>\n<p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule...</p>",
  "num_flashcards": 10,
  "subject": "Biologie",
  "grade": 6
}
```

**Field Descriptions:**
- `student_version` (string, required): The HTML content from `/api/generate-lecture` endpoint
- `num_flashcards` (int, required): Number of flashcards to generate (1-50)
- `subject` (string, optional): Subject name for context
- `grade` (int, optional): Grade level for context

### Response

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "flashcards": [
      {
        "flashcard_text": "Ce este celula?",
        "answer": "Celula este cea mai mică unitate structurală și funcțională a vieții. Toate organismele vii sunt formate din una sau mai multe celule."
      },
      {
        "flashcard_text": "Nucleul celulei conține ______ și controlează funcțiile celulare.",
        "answer": "ADN (material genetic)"
      },
      {
        "flashcard_text": "Care sunt cele trei componente principale ale unei celule?",
        "answer": "Membrana celulară, citoplasma și nucleul."
      },
      {
        "flashcard_text": "Ce rol are membrana celulară?",
        "answer": "Membrana celulară protejează celula și controlează ce intră și iese din ea, funcționând ca un filtru selectiv."
      },
      {
        "flashcard_text": "Citoplasma este ______ în care plutesc organitele celulare.",
        "answer": "o substanță gelatinoasă"
      },
      {
        "flashcard_text": "Care este diferența principală între celula animală și celula vegetală?",
        "answer": "Celula vegetală are perete celular rigid și cloroplaste pentru fotosinteză, în timp ce celula animală nu are aceste structuri."
      },
      {
        "flashcard_text": "De ce plantele sunt verzi?",
        "answer": "Plantele sunt verzi datorită clorofilei din cloroplaste, care este necesară pentru fotosinteză."
      },
      {
        "flashcard_text": "Enumeră patru funcții ale celulei.",
        "answer": "Nutriția, respirația celulară, reproducerea și eliminarea deșeurilor."
      },
      {
        "flashcard_text": "Ce este respirația celulară?",
        "answer": "Respirația celulară este procesul prin care celula obține energie din substanțele nutritive, având loc în mitocondrii."
      },
      {
        "flashcard_text": "De ce celula este considerată \"unitatea funcțională\" a vieții?",
        "answer": "Pentru că toate procesele vitale (nutriție, respirație, reproducere) au loc la nivel celular."
      }
    ],
    "count": 10,
    "subject": "Biologie",
    "grade": 6
  }
}
```

**Field Descriptions in Response:**
- `success` (boolean): Indicates if the request was successful
- `data.flashcards` (array): Array of flashcard objects
  - `flashcard_text` (string): The question, statement to complete, or prompt
  - `answer` (string): The complete answer or explanation
- `data.count` (int): Actual number of flashcards generated
- `data.subject` (string): Subject name
- `data.grade` (int): Grade level

**Error Response (400 Bad Request):**
```json
{
  "error": "Missing required parameter: student_version is required"
}
```

**Error Response (400 Bad Request - Invalid Range):**
```json
{
  "error": "num_flashcards must be between 1 and 50"
}
```

**Error Response (500 Internal Server Error):**
```json
{
  "error": "Content is too short to generate flashcards (minimum 100 characters)"
}
```

### cURL Example
```bash
curl -X POST http://localhost:5000/api/generate-flashcards \
  -H "Content-Type: application/json" \
  -d '{
    "student_version": "<h1>Celula</h1><p>Celula este cea mai mică unitate vie...</p>",
    "num_flashcards": 10,
    "subject": "Biologie",
    "grade": 6
  }'
```

### JavaScript Fetch Example
```javascript
fetch('http://localhost:5000/api/generate-flashcards', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    student_version: studentVersionHTML,  // From /api/generate-lecture
    num_flashcards: 10,
    subject: 'Biologie',
    grade: 6
  })
})
  .then(response => response.json())
  .then(data => {
    const flashcards = data.data.flashcards;
    const count = data.data.count;
    
    console.log(`Generated ${count} flashcards`);
    
    // Display flashcards
    flashcards.forEach((card, index) => {
      console.log(`\nFlashcard ${index + 1}:`);
      console.log(`Q: ${card.flashcard_text}`);
      console.log(`A: ${card.answer}`);
    });
  })
  .catch(error => console.error('Error:', error));
```

### Complete Workflow with Flashcards

```javascript
// Step 1: Generate lecture
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

// Step 2: Generate flashcards from the lesson
const flashcardsResponse = await fetch('http://localhost:5000/api/generate-flashcards', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_version: studentVersion,
    num_flashcards: 10,
    subject: 'Biologie',
    grade: 6
  })
});

const flashcardsData = await flashcardsResponse.json();
const flashcards = flashcardsData.data.flashcards;

// Display in your flashcard UI
flashcards.forEach((card, index) => {
  createFlashcardElement(card.flashcard_text, card.answer, index);
});
```

**Important Notes:**

1. **Flashcard Types**: The AI generates various types of flashcards:
   - Direct questions: "Ce este...?", "Care sunt...?"
   - Fill-in-the-blank: "______ este cea mai mică unitate a vieții."
   - Comparisons: "Care este diferența între X și Y?"
   - Definitions: "Defineşte conceptul de..."
   - Applications: "Dă un exemplu de..."

2. **Content Coverage**: Flashcards cover all major concepts from the lesson in logical order.

3. **Number of Flashcards**: 
   - Minimum: 1 flashcard
   - Maximum: 50 flashcards per request
   - Recommended: 10-15 flashcards for a standard lesson

4. **Content Length**: The student_version must be at least 100 characters long. For best results, use complete lesson content with multiple sections.

5. **Processing Time**: Flashcard generation typically takes 5-15 seconds depending on the number requested.

6. **Answer Quality**: Answers are:
   - Clear and concise
   - Accurate to the lesson content
   - Written in Romanian
   - Age-appropriate for the grade level

7. **Use Cases**:
   - Study tools for students
   - Quick review before tests
   - Spaced repetition learning apps
   - Digital flashcard platforms
   - Mobile learning applications

8. **Integration**: Perfect for:
   - Flashcard apps (Anki, Quizlet-style)
   - Learning management systems
   - Student portals
   - Mobile education apps

---


