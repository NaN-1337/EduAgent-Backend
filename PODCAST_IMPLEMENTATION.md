# Podcast Generation Implementation

## Overview

The podcast generation feature creates educational audio content from lecture materials using AI-powered dialogue generation and text-to-speech conversion.

## Architecture

### Components

1. **podcast_service.py**: Core service implementing:
   - Dialogue generation using OpenAI GPT-4o
   - Text-to-speech conversion using Async.ai API
   - Audio concatenation using ffmpeg
   - MP3 export with optimal settings

2. **app.py**: Flask endpoint `/api/generate-podcast`
   - Request validation
   - Service orchestration
   - Response formatting (JSON or direct audio download)

3. **Dependencies**: 
   - `langchain-openai`: GPT-4o dialogue generation
   - `requests`: Async.ai API calls
   - `ffmpeg`: Audio processing and concatenation (external binary)
   - `python-dotenv`: Environment configuration

## Features

### Dialogue Generation
- **Model**: OpenAI GPT-4o (more creative than gpt-4o-mini)
- **Temperature**: 0.7 (balanced creativity)
- **Format**: JSON array with speaker/text pairs
- **Characters**:
  - **Ana** (teacher): Female voice, explains concepts
  - **Mihai** (student): Male voice, asks questions
- **Duration Control**: ~150 words/minute for natural pacing
- **Content**: Age-appropriate dialogue based on grade level

### Text-to-Speech
- **Provider**: Async.ai API v1
- **Endpoint**: `https://async.ai/api/text_to_speech`
- **Authentication**: `x-api-key` header
- **Voices**:
  - Female (Ana): Configurable via `ASYNC_AI_VOICE_FEMALE`
  - Male (Mihai): Configurable via `ASYNC_AI_VOICE_MALE`
- **Output Format**: MP3, 44.1kHz sample rate

### Audio Processing
- **Tool**: ffmpeg (direct binary calls via subprocess)
- **Concatenation**: Sequential with silence between turns using ffmpeg concat demuxer
- **Silence Generation**: ffmpeg anullsrc filter (44.1kHz stereo)
- **Silence Duration**: Configurable (default 500ms)
- **Temporary Files**: Uses tempfile.TemporaryDirectory for intermediate files
- **Output Format**: MP3 with copy codec (preserves original quality)

## API Endpoint

### Request
```http
POST /api/generate-podcast
Content-Type: application/json

{
  "student_version": "<h1>Title</h1><p>Content...</p>",
  "teacher_version": "<h1>Title</h1><div class=\"teacher-note\">...</div>",
  "grade": 6,
  "subject": "Biologie",
  "target_duration": 300,
  "return_dialogue": true,
  "silence_between_turns": 500
}
```

### Response (with dialogue)
```json
{
  "success": true,
  "data": {
    "audio_base64": "SUQzBAAAAAAAI1RTU0U...",
    "audio_size_bytes": 245632,
    "dialogue": [
      {
        "speaker": "Ana",
        "text": "Bună, Mihai! Astăzi vom învăța despre..."
      },
      {
        "speaker": "Mihai",
        "text": "Bună, Ana! Da, sunt foarte curios..."
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

### Response (direct download)
When `return_dialogue: false`:
- Content-Type: `audio/mpeg`
- Content-Disposition: `attachment; filename="podcast_Biologie_6.mp3"`
- Body: Raw MP3 audio

## Configuration

### Environment Variables

Required:
```env
OPENAI_API_KEY=sk-...
ASYNC_AI_API_KEY=sk-...
```

Optional:
```env
ASYNC_AI_VOICE_FEMALE=ana
ASYNC_AI_VOICE_MALE=mihai
```

### Service Initialization

```python
# In app.py
try:
    from podcast_service import PodcastService
    podcast_service = PodcastService()
    print("✓ Podcast service initialized")
except Exception as e:
    print(f"⚠ Podcast service not available: {e}")
    podcast_service = None
```

## Workflow

1. **Receive Request**: Student version + teacher version + metadata
2. **Extract Content**: Parse HTML to extract text content
3. **Generate Dialogue**: 
   - Use GPT-4o to create conversation between Ana and Mihai
   - Target specific duration based on `target_duration`
   - Format as JSON with speaker/text pairs
4. **Convert to Speech**:
   - For each dialogue turn:
     - Determine speaker (Ana or Mihai)
     - Call Async.ai TTS API with appropriate voice
     - Receive MP3 audio bytes
     - Save to temporary file (turn_001.mp3, turn_002.mp3, etc.)
5. **Generate Silence** (if needed):
   - Use ffmpeg to create silence.mp3 with specified duration
   - Command: `ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t <duration> silence.mp3`
6. **Concatenate Audio**:
   - Create concat list file for ffmpeg
   - Interleave audio files with silence files
   - Use ffmpeg concat demuxer: `ffmpeg -f concat -safe 0 -i concat_list.txt -c copy output.mp3`
7. **Export**:
   - Read final MP3 file from temporary directory
   - Get duration using ffprobe
   - Clean up temporary files automatically
   - Return as base64 or direct download

## Error Handling

### Service Not Configured (503)
```json
{
  "error": "Podcast service not configured. Please add ASYNC_AI_API_KEY to your .env file."
}
```

### Missing Parameters (400)
```json
{
  "error": "Missing required parameters: student_version and teacher_version are required"
}
```

### Duration Validation (400)
```json
{
  "error": "target_duration must be between 60 and 1800 seconds"
}
```

### Internal Error (500)
```json
{
  "error": "Internal server error: [details]"
}
```

## Performance Considerations

### Generation Time
- **GPT-4o Dialogue**: ~30-60 seconds
- **TTS Conversion**: ~5-10 seconds per turn (10 turns = ~50-100 seconds)
- **Audio Processing**: ~5-10 seconds
- **Total**: ~2-5 minutes for 5-minute podcast

### Optimization Strategies
1. **Parallel TTS**: Could convert multiple turns concurrently
2. **Caching**: Store generated dialogues for reuse
3. **Streaming**: Stream audio segments as they're generated
4. **Progress Updates**: WebSocket for real-time status

## Testing

### Unit Test (standalone)
```bash
cd "d:\Hackathon Adobe"
python podcast_service.py
```

### Integration Test (via API)
```bash
# Start Flask server
python app.py

# In another terminal
curl -X POST http://localhost:5000/api/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "student_version": "<h1>Test</h1><p>Content...</p>",
    "teacher_version": "<h1>Test</h1><p>Content...</p>",
    "grade": 6,
    "subject": "Biologie",
    "target_duration": 180,
    "return_dialogue": true
  }'
```

### Expected Output
- JSON response with `audio_base64` and `dialogue` fields
- Audio file size: ~1-2 MB for 3-minute podcast
- Dialogue: 8-12 turns for 3-minute podcast

## Troubleshooting

### ffmpeg Not Found Error
```powershell
# Install ffmpeg on Windows
choco install ffmpeg
# Or
winget install ffmpeg
# Or download from https://ffmpeg.org/download.html

# Verify installation
ffmpeg -version
ffprobe -version
```

Note: Make sure ffmpeg and ffprobe are in your system PATH.

### Async.ai API Error
- Verify API key is valid
- Check API credits/quota
- Ensure internet connectivity
- Review Async.ai API status

### Audio Quality Issues
- Increase bitrate in export (currently 192k)
- Adjust sample rate (currently 44.1kHz)
- Reduce silence between turns for faster pacing
- Use higher-quality voice models

### Dialogue Generation Issues
- Increase temperature for more creativity (currently 0.7)
- Adjust target_duration for different content lengths
- Modify prompt template in DIALOGUE_PROMPT_TEMPLATE
- Check GPT-4o API availability

## Future Enhancements

1. **Multiple Languages**: Support for English, French, etc.
2. **Voice Selection**: Allow custom voice selection per speaker
3. **Background Music**: Add subtle educational background music
4. **Sound Effects**: Include sound effects for engagement
5. **Chapters**: Add MP3 chapter markers for navigation
6. **Subtitles**: Generate SRT/VTT subtitle files
7. **Speed Control**: Allow playback speed adjustment
8. **Podcast Feed**: Generate RSS feed for podcast distribution
9. **Analytics**: Track listening time and engagement
10. **A/B Testing**: Test different dialogue styles

## Security Considerations

1. **API Key Protection**: Never expose in client-side code
2. **Rate Limiting**: Implement rate limits to prevent abuse
3. **Input Validation**: Sanitize HTML content before processing
4. **File Size Limits**: Cap maximum audio file size
5. **Timeout Protection**: Set timeouts for long-running operations
6. **Error Messages**: Don't expose sensitive information in errors

## Documentation References

- [Async.ai API Documentation](https://docs.async.ai/text-to-speech)
- [OpenAI GPT-4o Documentation](https://platform.openai.com/docs/models/gpt-4o)
- [ffmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Flask Documentation](https://flask.palletsprojects.com/)

## Credits

- **AI Models**: OpenAI GPT-4o for dialogue generation
- **TTS Service**: Async.ai for text-to-speech conversion
- **Audio Processing**: ffmpeg for audio manipulation
- **Framework**: Flask REST API
