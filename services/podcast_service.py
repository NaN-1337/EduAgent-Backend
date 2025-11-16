"""
Podcast Service - Generate educational podcasts with dialogue and text-to-speech.
"""
import os
import json
import requests
import subprocess
import tempfile
import shutil
from typing import Dict, List, Tuple
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from config import Config


class PodcastService:
    """Service to generate educational podcasts with AI dialogue and OpenAI TTS."""
    
    # Prompt for generating podcast dialogue
    DIALOGUE_PROMPT_TEMPLATE = """You are an expert educational content creator specializing in creating engaging podcast dialogues for Romanian students.

Given the following educational content, create a natural, engaging conversation between two podcast hosts discussing the topic. The conversation should be educational, clear, and appropriate for the target grade level.

Student Version Content:
{student_content}

Teacher Version Content (for additional context):
{teacher_content}

Target Grade: {grade}
Subject: {subject}

Your task is to create a podcast dialogue between two hosts:
- Host 1 (Ana): An enthusiastic teacher who explains concepts clearly
- Host 2 (Mihai): A curious student representative who asks good questions

Guidelines:
1. Create a natural, conversational dialogue in Romanian
2. Start with a friendly introduction
3. Break down complex concepts into digestible parts
4. Use the student asking questions to address common confusions
5. Include real-world examples and analogies
6. Keep each speaking turn to 2-4 sentences (not too long)
7. Make it engaging and educational
8. End with a summary and conclusion
9. Total dialogue should be approximately {target_duration} seconds of speech (about {word_count} words)

Output the dialogue as a JSON array with this exact format:
{{
    "dialogue": [
        {{
            "speaker": "Ana",
            "text": "Bună ziua tuturor! Astăzi vom explora un subiect fascinant..."
        }},
        {{
            "speaker": "Mihai",
            "text": "Salut Ana! Sunt foarte curios să aflu mai multe despre..."
        }}
    ]
}}

Generate the complete podcast dialogue now in Romanian:"""
    
    def __init__(
        self,
        openai_api_key: str = None,
        model_name: str = None
    ):
        """
        Initialize the Podcast Service.
        
        Args:
            openai_api_key: OpenAI API key for dialogue generation and TTS
            model_name: OpenAI model name for dialogue generation
        """
        self.openai_api_key = openai_api_key or Config.OPENAI_API_KEY
        
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please add it to your .env file."
            )
        
        # Find ffmpeg and ffprobe executables
        self.ffmpeg_path = shutil.which('ffmpeg')
        self.ffprobe_path = shutil.which('ffprobe')
        
        # If not found in PATH, try common installation locations
        if not self.ffmpeg_path:
            common_paths = [
                r'C:\ffmpeg\bin\ffmpeg.exe',
                r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
                os.path.expanduser(r'~\scoop\apps\ffmpeg\current\bin\ffmpeg.exe'),
                os.path.expanduser(r'~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe'),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    self.ffmpeg_path = path
                    break
        
        if not self.ffprobe_path:
            common_paths = [
                r'C:\ffmpeg\bin\ffprobe.exe',
                r'C:\Program Files\ffmpeg\bin\ffprobe.exe',
                os.path.expanduser(r'~\scoop\apps\ffmpeg\current\bin\ffprobe.exe'),
                os.path.expanduser(r'~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffprobe.exe'),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    self.ffprobe_path = path
                    break
        
        if not self.ffmpeg_path or not self.ffprobe_path:
            raise ValueError(
                f"ffmpeg/ffprobe not found. Please restart your Python process/IDE after installing ffmpeg. "
                f"ffmpeg={self.ffmpeg_path}, ffprobe={self.ffprobe_path}"
            )
        
        self.model_name = model_name or "gpt-4o"
        
        # Initialize OpenAI for dialogue generation
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=0.7,  # More creative for dialogue
            openai_api_key=self.openai_api_key,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        self.prompt = PromptTemplate(
            template=self.DIALOGUE_PROMPT_TEMPLATE,
            input_variables=["student_content", "teacher_content", "grade", "subject", "target_duration", "word_count"]
        )
        
        # Voice configuration for OpenAI TTS
        # Available voices: alloy, echo, fable, onyx, nova, shimmer
        # For Romanian: "nova" (female) and "onyx" (male) tend to handle multilingual content well
        self.voices = {
            "Ana": os.getenv("OPENAI_VOICE_FEMALE", "nova"),     # Female voice - warm, clear
            "Mihai": os.getenv("OPENAI_VOICE_MALE", "onyx")      # Male voice - deep, authoritative
        }
        
        # Use tts-1-hd for higher quality (better for Romanian pronunciation)
        self.tts_model = "tts-1-hd"
    
    def generate_dialogue(
        self,
        student_content: str,
        teacher_content: str,
        grade: int,
        subject: str,
        target_duration: int = 300  # 5 minutes default
    ) -> List[Dict[str, str]]:
        """
        Generate podcast dialogue using GPT-4o.
        
        Args:
            student_content: HTML content from student version
            teacher_content: HTML content from teacher version
            grade: Grade level
            subject: Subject name
            target_duration: Target duration in seconds
            
        Returns:
            List of dialogue turns with speaker and text
        """
        # Estimate word count (assuming ~150 words per minute of speech)
        word_count = int((target_duration / 60) * 150)
        
        print(f"Generating podcast dialogue (~{target_duration}s, ~{word_count} words)...")
        
        # Format the prompt
        formatted_prompt = self.prompt.format(
            student_content=student_content,
            teacher_content=teacher_content,
            grade=grade,
            subject=subject,
            target_duration=target_duration,
            word_count=word_count
        )
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse JSON from response
        try:
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            dialogue_data = json.loads(response_text)
            dialogue = dialogue_data.get("dialogue", [])
            
            print(f"✓ Generated dialogue with {len(dialogue)} turns")
            return dialogue
            
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse dialogue JSON: {e}")
            print(f"Raw response: {response_text[:500]}...")
            raise Exception(f"Failed to parse dialogue from AI response: {str(e)}")
    
    def text_to_speech(
        self,
        text: str,
        voice: str,
        model: str = "tts-1-hd"
    ) -> bytes:
        """
        Convert text to speech using OpenAI TTS API.
        
        Args:
            text: Text to convert to speech
            voice: OpenAI voice name (alloy, echo, fable, onyx, nova, shimmer)
            model: Model to use (tts-1 or tts-1-hd for higher quality)
            
        Returns:
            Audio data in bytes (MP3 format)
        """
        from openai import OpenAI
        
        client = OpenAI(api_key=self.openai_api_key)
        
        try:
            response = client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format="mp3"
            )
            
            # Response is already bytes in MP3 format
            return response.content
            
        except Exception as e:
            error_msg = f"Failed to generate speech with OpenAI TTS: {str(e)}"
            raise Exception(error_msg)
    
    def create_podcast(
        self,
        student_content: str,
        teacher_content: str,
        grade: int,
        subject: str,
        target_duration: int = 300,
        silence_between_turns: int = 500,  # milliseconds
        teacher_id: str = None,
        lecture_id: str = None,
        upload_to_firebase: bool = False
    ) -> Dict:
        """
        Create a complete podcast from lecture content.
        
        Args:
            student_content: HTML content from student version
            teacher_content: HTML content from teacher version
            grade: Grade level
            subject: Subject name
            target_duration: Target duration in seconds
            silence_between_turns: Silence duration between speakers in ms
            teacher_id: Teacher ID for Firebase path (required if upload_to_firebase=True)
            lecture_id: Lecture ID for Firebase path (required if upload_to_firebase=True)
            upload_to_firebase: If True, upload to Firebase Storage instead of local save
            
        Returns:
            Dictionary with audio_bytes, dialogue, and optional firebase_info:
            {
                'audio_bytes': bytes,
                'dialogue': List[Dict],
                'duration_seconds': float,
                'size_bytes': int,
                'firebase_info': Dict (if uploaded to Firebase)
            }
        """
        # Step 1: Generate dialogue
        dialogue = self.generate_dialogue(
            student_content=student_content,
            teacher_content=teacher_content,
            grade=grade,
            subject=subject,
            target_duration=target_duration
        )
        
        # Step 2: Generate TTS for each dialogue turn
        print(f"\nGenerating speech for {len(dialogue)} dialogue turns...")
        
        # Create temporary directory for audio files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            audio_files = []
            
            for i, turn in enumerate(dialogue, 1):
                speaker = turn.get("speaker")
                text = turn.get("text")
                
                if not speaker or not text:
                    print(f"Warning: Skipping invalid dialogue turn: {turn}")
                    continue
                
                # Get voice for speaker
                voice = self.voices.get(speaker)
                if not voice:
                    print(f"Warning: No voice for speaker '{speaker}', using default")
                    voice = self.voices.get("Ana")
                
                print(f"  [{i}/{len(dialogue)}] {speaker}: Generating speech...")
                
                try:
                    # Generate speech using OpenAI TTS
                    audio_bytes = self.text_to_speech(text, voice, model=self.tts_model)
                    
                    # Save to temporary file
                    audio_file = temp_path / f"turn_{i:03d}.mp3"
                    with open(audio_file, 'wb') as f:
                        f.write(audio_bytes)
                    
                    audio_files.append(str(audio_file))
                    print(f"      ✓ Generated {len(audio_bytes)} bytes")
                    
                except Exception as e:
                    print(f"      ✗ Error generating speech for turn {i}: {e}")
                    # Continue with next turn instead of failing completely
                    continue
            
            if not audio_files:
                raise Exception("Failed to generate any audio segments")
            
            # Step 3: Concatenate all audio segments using ffmpeg
            print(f"\nCombining {len(audio_files)} audio segments with ffmpeg...")
            
            # Create silence file if needed
            silence_file = None
            if silence_between_turns > 0 and len(audio_files) > 1:
                silence_file = temp_path / "silence.mp3"
                silence_duration = silence_between_turns / 1000.0  # Convert ms to seconds
                
                # Generate silence using ffmpeg
                subprocess.run([
                    self.ffmpeg_path, '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo',
                    '-t', str(silence_duration), '-q:a', '2', '-y', str(silence_file)
                ], check=True, capture_output=True)
            
            # Create concat file list
            concat_file = temp_path / "concat_list.txt"
            with open(concat_file, 'w', encoding='utf-8') as f:
                for i, audio_file in enumerate(audio_files):
                    f.write(f"file '{audio_file}'\n")
                    # Add silence between turns (except after last turn)
                    if silence_file and i < len(audio_files) - 1:
                        f.write(f"file '{silence_file}'\n")
            
            # Concatenate using ffmpeg
            output_file = temp_path / "final_podcast.mp3"
            subprocess.run([
                self.ffmpeg_path, '-f', 'concat', '-safe', '0', '-i', str(concat_file),
                '-c', 'copy', '-y', str(output_file)
            ], check=True, capture_output=True)
            
            # Read final audio
            with open(output_file, 'rb') as f:
                final_audio_bytes = f.read()
            
            # Get duration using ffprobe
            result = subprocess.run([
                self.ffprobe_path, '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', str(output_file)
            ], capture_output=True, text=True, check=True)
            
            duration_seconds = float(result.stdout.strip())
            
            print(f"✓ Podcast created successfully!")
            print(f"  Duration: {duration_seconds:.1f} seconds ({duration_seconds/60:.1f} minutes)")
            print(f"  Size: {len(final_audio_bytes) / 1024 / 1024:.2f} MB")
            print(f"  Turns: {len(dialogue)}")
            
            result = {
                'audio_bytes': final_audio_bytes,
                'dialogue': dialogue,
                'duration_seconds': duration_seconds,
                'size_bytes': len(final_audio_bytes)
            }
            
            # Upload to Firebase if requested
            if upload_to_firebase:
                if not teacher_id or not lecture_id:
                    raise ValueError("teacher_id and lecture_id are required when upload_to_firebase=True")
                
                from firebase_service import FirebaseService
                
                if not FirebaseService.is_available():
                    raise Exception("Firebase Storage is not available. Please configure Firebase credentials.")
                
                # Generate filename with timestamp
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"podcast_{timestamp}.mp3"
                
                # Construct Firebase Storage path: {teacherID}/{grade}/{lectureID}/podcast_{timestamp}.mp3
                firebase_path = f"{teacher_id}/{grade}/{lecture_id}/{filename}"
                
                print(f"\nUploading to Firebase Storage: {firebase_path}")
                
                # Prepare metadata
                metadata = {
                    'subject': subject,
                    'grade': str(grade),
                    'teacher_id': teacher_id,
                    'lecture_id': lecture_id,
                    'duration_seconds': str(duration_seconds),
                    'turns_count': str(len(dialogue)),
                    'generated_at': timestamp
                }
                
                # Upload bytes directly to Firebase (no local save)
                firebase_info = FirebaseService.upload_bytes(
                    file_bytes=final_audio_bytes,
                    destination_path=firebase_path,
                    content_type='audio/mpeg',
                    make_public=True,  # Make publicly accessible
                    metadata=metadata
                )
                
                result['firebase_info'] = firebase_info
                print(f"✓ Podcast uploaded to Firebase successfully")
            
            return result


if __name__ == "__main__":
    # Test the service
    print("Testing Podcast Service...\n")
    
    try:
        service = PodcastService()
        
        # Test content
        student_content = """
        <h1>Celula - unitatea structurală și funcțională a vieții</h1>
        <h2>Introducere</h2>
        <p>Celula este cea mai mică unitate vie a organismelor. Toate ființele vii sunt alcătuite din una sau mai multe celule.</p>
        <h2>Structura celulei</h2>
        <p>Celula are trei componente principale: membrana celulară, citoplasma și nucleul.</p>
        """
        
        teacher_content = student_content + "\n<p>Note pentru profesor: Subliniați importanța celulei ca unitate fundamentală.</p>"
        
        print("Generating podcast...")
        audio_bytes, dialogue = service.create_podcast(
            student_content=student_content,
            teacher_content=teacher_content,
            grade=6,
            subject="Biologie",
            target_duration=120  # 2 minutes for testing
        )
        
        # Save to file for testing
        with open("test_podcast.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print("\n✓ Test podcast saved to test_podcast.mp3")
        print(f"\nDialogue preview:")
        for i, turn in enumerate(dialogue[:3], 1):
            print(f"{i}. {turn['speaker']}: {turn['text'][:80]}...")
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease add these to your .env file:")
        print("ASYNC_AI_API_KEY=sk-xxxxx")
        print("ASYNC_AI_VOICE_FEMALE=voice-id-1  # Optional: female voice ID")
        print("ASYNC_AI_VOICE_MALE=voice-id-2    # Optional: male voice ID")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
