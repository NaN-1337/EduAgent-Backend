"""
Presenton Service - Generate presentations using Presenton API.
"""
import os
import requests
from typing import Dict, Optional
import unicodedata


class PresentonService:
    """Service to generate presentations using Presenton API."""
    
    BASE_URL = "https://api.presenton.ai/api/v1/ppt"
    
    # Romanian diacritic mapping: incorrect/similar -> correct
    ROMANIAN_DIACRITICS_MAP = {
        'ş': 'ș',  # s-cedilla to s-comma
        'Ş': 'Ș',  # S-cedilla to S-comma
        'ţ': 'ț',  # t-cedilla to t-comma
        'Ţ': 'Ț',  # T-cedilla to T-comma
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Presenton service.
        
        Args:
            api_key: Presenton API key. If None, reads from environment variable.
        """
        self.api_key = api_key or os.getenv("PRESENTON_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "PRESENTON_API_KEY not found. Please add it to your .env file."
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8"
        }
    
    def normalize_romanian_text(self, text: str) -> str:
        """
        Normalize text to use correct Romanian diacritics.
        
        Romanian uses comma-below diacritics (ș, ț) not cedilla diacritics (ş, ţ).
        This method ensures the correct Unicode characters are used.
        
        Args:
            text: Input text that may contain incorrect diacritics
            
        Returns:
            Text with correct Romanian diacritics
        """
        # Replace incorrect diacritics with correct ones
        for incorrect, correct in self.ROMANIAN_DIACRITICS_MAP.items():
            text = text.replace(incorrect, correct)
        
        # Ensure text is in NFC (Canonical Composition) form
        # This combines base characters with diacritics into single characters
        text = unicodedata.normalize('NFC', text)
        
        return text
    
    def generate_presentation(
        self,
        content: str,
        n_slides: int = 8,
        language: str = "Romanian",
        template: str = "general",
        tone: str = "educational",
        verbosity: str = "standard",
        export_as: str = "pptx",
        include_title_slide: bool = True,
        image_type: str = "stock",
        theme: Optional[str] = None
    ) -> Dict:
        """
        Generate a presentation from text content.
        
        Args:
            content: The text content for generating the presentation
            n_slides: Number of slides to generate (default: 8)
            language: Language for the presentation (default: "Romanian")
            template: Template to use (general, modern, standard, swift)
            tone: Tone for text (default, casual, professional, funny, educational, sales_pitch)
            verbosity: How verbose the text should be (concise, standard, text-heavy)
            export_as: Export format (pptx or pdf)
            include_title_slide: Whether to include a title slide
            image_type: Type of image (stock or ai-generated)
            theme: Custom theme name (optional)
            
        Returns:
            Dictionary with presentation_id, path, edit_path, and credits_consumed
        """
        # Normalize Romanian diacritics in the content
        content = self.normalize_romanian_text(content)
        
        endpoint = f"{self.BASE_URL}/presentation/generate"
        
        payload = {
            "content": content,
            "n_slides": n_slides,
            "language": language,
            "template": template,
            "tone": tone,
            "verbosity": verbosity,
            "export_as": export_as,
            "include_title_slide": include_title_slide,
            "image_type": image_type,
            "markdown_emphasis": True,
            "web_search": False,
            "include_table_of_contents": False
        }
        
        # Add theme if provided
        if theme:
            payload["theme"] = theme
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=payload,
                timeout=120  # 2 minutes timeout for generation
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("Presentation generation timed out. The content might be too long.")
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to generate presentation: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f" - {e.response.text}"
            raise Exception(error_msg)
    
    def get_presentation_with_slides(self, presentation_id: str) -> Dict:
        """
        Get a presentation and its slides by ID.
        
        Args:
            presentation_id: UUID of the presentation
            
        Returns:
            Dictionary with presentation details and parsed slides data
        """
        endpoint = f"{self.BASE_URL}/presentation/{presentation_id}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to retrieve presentation: {str(e)}"
            if hasattr(e.response, 'text'):
                error_msg += f" - {e.response.text}"
            raise Exception(error_msg)
    
    def generate_and_get_slides(
        self,
        content: str,
        n_slides: int = 8,
        language: str = "Romanian",
        **kwargs
    ) -> Dict:
        """
        Generate a presentation and retrieve its parsed slides data.
        
        This is a convenience method that combines generate_presentation and
        get_presentation_with_slides.
        
        Args:
            content: The text content for generating the presentation
            n_slides: Number of slides to generate
            language: Language for the presentation
            **kwargs: Additional arguments passed to generate_presentation
            
        Returns:
            Dictionary containing:
            - presentation: Basic presentation info (id, path, edit_path, credits)
            - slides: Parsed slides data with content for each slide
        """
        # Generate the presentation
        print(f"Generating presentation with {n_slides} slides...")
        generation_result = self.generate_presentation(
            content=content,
            n_slides=n_slides,
            language=language,
            **kwargs
        )
        
        presentation_id = generation_result["presentation_id"]
        print(f"Presentation generated with ID: {presentation_id}")
        
        # Retrieve the presentation with slides
        print("Retrieving presentation slides data...")
        full_data = self.get_presentation_with_slides(presentation_id)
        
        # Parse slides into a simpler format
        slides_parsed = []
        for slide in full_data.get("slides", []):
            slides_parsed.append({
                "slide_index": slide.get("index"),
                "layout": slide.get("layout"),
                "html_content": slide.get("html_content"),
                "speaker_note": slide.get("speaker_note"),
                "content": slide.get("content", {})
            })
        
        return {
            "presentation": {
                "id": generation_result["presentation_id"],
                "download_url": generation_result["path"],
                "edit_url": generation_result["edit_path"],
                "credits_consumed": generation_result["credits_consumed"],
                "n_slides": full_data.get("n_slides"),
                "language": full_data.get("language"),
                "title": full_data.get("title")
            },
            "slides": slides_parsed
        }


if __name__ == "__main__":
    # Test the service
    print("Testing Presenton Service...\n")
    
    try:
        service = PresentonService()
        
        # Test content
        test_content = """
        <h1>Celula - unitatea structurală și funcțională a vieții</h1>
        <h2>Introducere</h2>
        <p>Celula este cea mai mică unitate vie a organismelor.</p>
        <h2>Structura celulei</h2>
        <p>Celula are trei componente principale: membrana celulară, citoplasma și nucleul.</p>
        """
        
        print("Generating presentation...")
        result = service.generate_and_get_slides(
            content=test_content,
            n_slides=5,
            language="Romanian"
        )
        
        print("\n" + "="*60)
        print("Presentation Info:")
        print("="*60)
        print(f"ID: {result['presentation']['id']}")
        print(f"Download URL: {result['presentation']['download_url']}")
        print(f"Edit URL: {result['presentation']['edit_url']}")
        print(f"Slides: {result['presentation']['n_slides']}")
        print(f"Credits: {result['presentation']['credits_consumed']}")
        
        print("\n" + "="*60)
        print(f"Parsed Slides ({len(result['slides'])} slides):")
        print("="*60)
        for slide in result['slides'][:3]:  # Show first 3 slides
            print(f"\nSlide {slide['slide_index']}:")
            print(f"  Layout: {slide['layout']}")
            if slide['html_content']:
                print(f"  HTML Preview: {slide['html_content'][:100]}...")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease add PRESENTON_API_KEY to your .env file:")
        print("PRESENTON_API_KEY=sk-presenton-xxxxx")
    except Exception as e:
        print(f"\n❌ Error: {e}")
