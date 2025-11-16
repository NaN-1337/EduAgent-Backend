"""
PDF Parser Service - Extract handwritten text from PDF and image submissions using GPT-4o Vision.
"""
import requests
import base64
import io
from typing import Dict, List
from pdf2image import convert_from_bytes
from openai import OpenAI
from config import Config


class PDFParserService:
    """
    Service for parsing handwritten homework submissions from PDF files or images (JPEG, PNG).
    Uses GPT-4o Vision API to extract text from images of PDF pages or direct image uploads.
    """
    
    def __init__(self):
        """Initialize the PDF parser service."""
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            base_url=Config.OPENAI_API_BASE
        )
        self.model = "gpt-4o"
        self.max_pages = 20  # Limit to prevent excessive API calls
    
    def download_file(self, url: str) -> tuple[bytes, str]:
        """
        Download PDF or image file from URL.
        
        Args:
            url: URL of the PDF or image file
            
        Returns:
            Tuple of (file content as bytes, content type)
            
        Raises:
            requests.RequestException: If download fails
        """
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        
        # Check if it's a supported file type
        supported_types = ['pdf', 'jpeg', 'jpg', 'png', 'image']
        url_lower = url.lower()
        
        is_supported = any(file_type in content_type for file_type in supported_types) or \
                      any(url_lower.endswith(f'.{ext}') for ext in ['pdf', 'jpg', 'jpeg', 'png'])
        
        if not is_supported:
            raise ValueError(f"URL does not point to a supported file (PDF, JPEG, PNG). Content-Type: {content_type}")
        
        return response.content, content_type
    
    def is_image(self, content_type: str, url: str) -> bool:
        """
        Check if the content is an image file.
        
        Args:
            content_type: The content type from HTTP headers
            url: The file URL
            
        Returns:
            True if it's an image file
        """
        image_types = ['jpeg', 'jpg', 'png', 'image']
        return any(img_type in content_type.lower() for img_type in image_types) or \
               any(url.lower().endswith(f'.{ext}') for ext in ['jpg', 'jpeg', 'png'])
    
    def pdf_to_images(self, pdf_bytes: bytes) -> List[bytes]:
        """
        Convert PDF pages to images.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            List of image bytes (JPEG format) for each page
        """
        # Convert PDF to images (one per page)
        images = convert_from_bytes(pdf_bytes, dpi=300, fmt='jpeg')
        
        # Limit number of pages
        if len(images) > self.max_pages:
            images = images[:self.max_pages]
        
        # Convert PIL images to bytes
        image_bytes_list = []
        for img in images:
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=95)
            image_bytes_list.append(img_byte_arr.getvalue())
        
        return image_bytes_list
    
    def encode_image(self, image_bytes: bytes) -> str:
        """
        Encode image bytes to base64 string.
        
        Args:
            image_bytes: Image content as bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def extract_text_from_image(self, image_base64: str, page_number: int) -> str:
        """
        Extract handwritten text from an image using GPT-4o Vision.
        
        Args:
            image_base64: Base64 encoded image
            page_number: Page number (for context)
            
        Returns:
            Extracted text from the image
        """
        prompt = f"""You are analyzing page {page_number} of a student's handwritten homework submission.

Your task is to accurately transcribe ALL handwritten text from this image, including:
- Exercise numbers and questions (if visible)
- Student's written solutions and answers
- Mathematical equations, formulas, or diagrams (describe them in text)
- Any notes, corrections, or annotations

Rules:
1. Transcribe exactly what is written, including mistakes or crossed-out text
2. For mathematical notation, use standard text representations (e.g., "x^2" for x squared, "√4" for square root of 4)
3. If text is unclear or illegible, write [ILLEGIBLE] and provide your best guess in brackets [maybe: ...]
4. Preserve the structure and order of the content
5. For diagrams or drawings, describe them briefly: [DIAGRAM: description]
6. Write in Romanian if the text is in Romanian

Output format:
Provide the transcribed text in a clear, organized manner. Start with "=== PAGE {page_number} ===" as a header."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.2  # Low temperature for accurate transcription
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"=== PAGE {page_number} ===\n[ERROR: Failed to extract text - {str(e)}]"
    
    def parse_pdf_submission(self, url: str) -> Dict:
        """
        Parse a PDF or image submission from URL and extract all handwritten text.
        
        Args:
            url: URL of the PDF or image submission
            
        Returns:
            Dictionary with:
                - success: bool
                - parsed_text: str (combined text from all pages)
                - page_count: int
                - pages: list of individual page texts
        """
        try:
            # Download file
            print(f"Downloading file from: {url}")
            file_bytes, content_type = self.download_file(url)
            print(f"Downloaded {len(file_bytes)} bytes, Content-Type: {content_type}")
            
            # Check if it's an image or PDF
            if self.is_image(content_type, url):
                print("Processing as image file...")
                # Treat the image as a single page
                images = [file_bytes]
            else:
                # Convert PDF to images
                print("Converting PDF to images...")
                images = self.pdf_to_images(file_bytes)
            
            page_count = len(images)
            print(f"Processing {page_count} image(s)...")
            
            # Extract text from each page
            print("Extracting text from images...")
            page_texts = []
            for i, img_bytes in enumerate(images, start=1):
                print(f"Processing page {i}/{page_count}...")
                img_base64 = self.encode_image(img_bytes)
                text = self.extract_text_from_image(img_base64, i)
                page_texts.append(text)
            
            # Combine all pages
            combined_text = "\n\n".join(page_texts)
            
            print("File parsing completed successfully")
            
            return {
                "success": True,
                "parsed_text": combined_text,
                "page_count": page_count,
                "pages": page_texts
            }
        
        except Exception as e:
            print(f"Error parsing file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "parsed_text": "",
                "page_count": 0,
                "pages": []
            }
