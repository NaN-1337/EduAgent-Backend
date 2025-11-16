# Quick Start Guide

## Setup (3 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Your OpenAI API Key
Edit the `.env` file and add your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Start the Chatbot
```bash
python main.py
```

The vector store with Romanian curriculum documents is already embedded and ready to use!

## Example Interaction

```
You: Generate a lesson plan for grade 6 biology about photosynthesis
Assistant: [AI generates structured lesson plan with slides and quiz]

You: Create a PowerPoint outline about cells
Assistant: [AI provides detailed outline ready for slides]

You: sources
[Shows which curriculum documents were used]

You: quit
```

## Tips

- The chatbot generates complete educational materials (lesson plans, slides, quizzes)
- Use `clear` to start a fresh conversation
- Use `sources` to see which curriculum documents were referenced
- All materials are aligned with Romanian Ministry of Education standards

## Need Help?

See `README.md` for full documentation.
