"""
Flashcards Service - Generate educational flashcards from lesson content.
"""
import re
import json
from typing import Dict, List
from openai import OpenAI
from config import Config


class FlashcardsService:
    """
    Service for generating flashcards from educational content.
    Uses GPT-4o to create question-answer pairs based on lesson material.
    """
    
    def __init__(self):
        """Initialize the flashcards service."""
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
        self.model = "gpt-4o"
        self.temperature = 0.7
    
    def _clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content for better processing.
        
        Args:
            html_content: HTML content from student version
            
        Returns:
            Clean text content
        """
        # Remove HTML tags
        clean_text = re.sub('<[^<]+?>', ' ', html_content)
        
        # Normalize whitespace
        clean_text = ' '.join(clean_text.split())
        
        return clean_text
    
    def generate_flashcards(
        self,
        student_version: str,
        num_flashcards: int,
        subject: str = "",
        grade: int = None
    ) -> Dict:
        """
        Generate flashcards from student lesson content.
        
        Args:
            student_version: HTML content from /api/generate-lecture
            num_flashcards: Number of flashcards to generate
            subject: Subject name (optional, for context)
            grade: Grade level (optional, for context)
            
        Returns:
            Dictionary with:
                - success: bool
                - flashcards: list of flashcard objects
                - count: int (actual number generated)
        """
        # Validate input
        if num_flashcards < 1:
            return {
                "success": False,
                "error": "Number of flashcards must be at least 1"
            }
        
        if num_flashcards > 50:
            return {
                "success": False,
                "error": "Maximum 50 flashcards per request"
            }
        
        # Clean HTML content
        clean_content = self._clean_html_content(student_version)
        
        if len(clean_content) < 100:
            return {
                "success": False,
                "error": "Content is too short to generate flashcards (minimum 100 characters)"
            }
        
        # Build the prompt
        subject_context = f" pentru {subject}" if subject else ""
        grade_context = f" (clasa {grade})" if grade else ""
        
        prompt = f"""Tu ești un profesor experimentat care creează flashcard-uri educaționale{subject_context}{grade_context}.

CONȚINUT LECȚIE:
{clean_content}

SARCINĂ:
Generează exact {num_flashcards} flashcard-uri bazate pe acest conținut.

TIPURI DE FLASHCARD-URI:
1. **Întrebări directe**: "Ce este...?", "Care sunt...?", "Cum funcționează...?"
2. **Afirmații de completat**: "______ este cea mai mică unitate a vieții."
3. **Comparații**: "Care este diferența între X și Y?"
4. **Definiții**: "Defineşte conceptul de..."
5. **Aplicații**: "Dă un exemplu de..."

REGULI:
- Acoperă toate conceptele importante din lecție
- Variază tipurile de flashcard-uri
- Răspunsurile trebuie să fie clare, concise și precise
- Folosește terminologia corectă din lecție
- Pentru concepte complexe, împarte în mai multe flashcard-uri simple
- Ordinea flashcard-urilor să urmeze logica lecției

FORMAT DE IEȘIRE (JSON):
Returnează un array JSON cu exact {num_flashcards} obiecte, fiecare având:
{{
  "flashcard_text": "Întrebarea sau afirmația de completat",
  "answer": "Răspunsul complet și clar"
}}

EXEMPLU:
[
  {{
    "flashcard_text": "Ce este celula?",
    "answer": "Celula este cea mai mică unitate structurală și funcțională a vieții. Toate organismele vii sunt formate din una sau mai multe celule."
  }},
  {{
    "flashcard_text": "Nucleul celulei conține ______ și controlează funcțiile celulare.",
    "answer": "ADN (material genetic)"
  }}
]

IMPORTANT: Returnează DOAR array-ul JSON, fără text suplimentar înainte sau după."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=3000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text
            
            # Parse JSON
            try:
                flashcards = json.loads(json_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response text: {response_text[:500]}")
                return {
                    "success": False,
                    "error": "Failed to parse flashcards from AI response"
                }
            
            # Validate structure
            if not isinstance(flashcards, list):
                return {
                    "success": False,
                    "error": "Invalid flashcards format: expected a list"
                }
            
            # Validate each flashcard
            valid_flashcards = []
            for i, card in enumerate(flashcards):
                if not isinstance(card, dict):
                    print(f"Warning: Flashcard {i} is not a dictionary, skipping")
                    continue
                
                if "flashcard_text" not in card or "answer" not in card:
                    print(f"Warning: Flashcard {i} missing required fields, skipping")
                    continue
                
                # Ensure fields are strings
                valid_flashcards.append({
                    "flashcard_text": str(card["flashcard_text"]),
                    "answer": str(card["answer"])
                })
            
            if len(valid_flashcards) == 0:
                return {
                    "success": False,
                    "error": "No valid flashcards were generated"
                }
            
            print(f"Successfully generated {len(valid_flashcards)} flashcards")
            
            return {
                "success": True,
                "flashcards": valid_flashcards,
                "count": len(valid_flashcards),
                "subject": subject,
                "grade": grade
            }
        
        except Exception as e:
            print(f"Error generating flashcards: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to generate flashcards: {str(e)}"
            }
