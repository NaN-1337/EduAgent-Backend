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

1. **Subject field**: In the second endpoint, the `subject` field must match the metadata in the vector store. Typically this is lowercase (e.g., "biologie", "matematică", "fizică").

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

4. **Loading states**: Both endpoints may take 5-15 seconds to generate responses (they're calling AI models). Make sure to show loading indicators in your UI.

5. **Answer format**: When a user selects "Altele" (Other) as an answer, they should be able to provide free-text input. Pass this custom text as the answer value.

6. **CORS**: The API has CORS enabled for all origins. In production, you may want to restrict this to your frontend domain.
