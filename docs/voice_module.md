"""Voice & Language Intelligence Module Documentation

## Overview

The Voice & Language Intelligence module enables artisans to describe their products through natural speech in their native language. The module handles the complete pipeline from audio input to structured product information using Gemini AI for speech-to-text and product attribute extraction.

## Module Responsibility

**Owner**: Voice & Language Intelligence team  
**Location**: `app/services/speech/`  
**Primary Function**: Convert artisan voice input → structured product information

## Pipeline (v2 - Gemini-Powered)

```
ARTISAN SPEECH (AUDIO FILE)
     ↓
[AudioProcessor] Validate audio file
     ↓
[GeminiClient] Speech-to-Text transcription
     ↓
ORIGINAL TRANSCRIPT
     ↓
[LanguageDetector] Detect language from text
     ↓
LANGUAGE CODE (e.g., "kn", "en")
     ↓
[GeminiClient] Normalize to English (if needed)
     ↓
NORMALIZED TRANSCRIPT
     ↓
[GeminiClient] AI-Powered Product Attribute Extraction
     ↓
STRUCTURED PRODUCT INFORMATION
     ↓
[Confidence Scoring] Per-field confidence calculation
     ↓
MISSING FIELD IDENTIFICATION
     ↓
VOICE_PROCESSING_RESULT (schema-compliant)
```

## Input Format

The module accepts input in the following structure:

```json
{
  "product_id": "ART-001",
  "audio": {
    "audio_id": "audio_001",
    "storage_path": "products/ART-001/audio_001.wav"
  }
}
```

### Input Specifications

- **product_id** (required): Unique artisan product identifier
- **audio** (required): Audio file metadata
  - **audio_id** (required): Unique identifier for this audio file
  - **storage_path** (required): Relative path to audio file in storage

**Important**: The module reads audio from the file system. The path is relative to `STORAGE_ROOT` configured in environment settings.

## Output Format

The module produces schema-compliant output:

```json
{
  "product_id": "ART-001",
  "product": {
    "name": "string or null",
    "category": "string or null",
    "subcategory": "string or null",
    "material": "string or null",
    "color": "string or null",
    "craft_type": "string or null",
    "description": "string or null",
    "dimensions": {
      "length": "number or null",
      "width": "number or null",
      "height": "number or null",
      "unit": "string or null"
    },
    "weight": {
      "value": "number or null",
      "unit": "string or null"
    },
    "usage": "string or null",
    "pattern": "string or null",
    "special_features": ["string array"],
    "production_time": "string or null"
  },
  "voice": {
    "language_code": "string or null",
    "original_transcript": "string or null",
    "translated_transcript": "string or null",
    "confidence": "0.0 to 1.0"
  },
  "missing_fields": ["array of field names"],
  "field_confidence": {
    "language_detection": "0.0 to 1.0",
    "speech_to_text": "0.0 to 1.0",
    "normalization": "0.0 to 1.0",
    ...per-field confidence scores...
  }
}
```

## Architecture (Modular Design)

The v2 implementation is organized into focused modules:

### Module Files

- **schemas.py** - Data models (ProductInfo, VoiceMetadata, etc.)
- **audio_processor.py** - Audio file validation and reading
- **gemini_client.py** - Gemini API wrapper for STT, extraction, normalization
- **language_detection.py** - Language detection from text
- **voice_processor.py** - Main orchestrator and legacy components
- **__init__.py** - Public API exports

### Core Components

#### 1. VoiceProcessor (Orchestrator)

Main entry point for the entire pipeline.

```python
from app.services.speech import VoiceProcessor

processor = VoiceProcessor(
    storage_root="data/uploads",
    gemini_api_key=None,  # Uses env var
    speech_model=None,    # Uses GEMINI_SPEECH_MODEL env var
    extraction_model=None # Uses GEMINI_CATALOG_MODEL env var
)

result = processor.process_from_input(input_data)
```

**Methods**:
- `process(product_id, audio_id, storage_path, transcript=None)`: Core processing
- `process_from_input(input_data, transcript=None)`: Standard interface
- `_build_product_info()`: Convert Gemini extraction to ProductInfo
- `_identify_missing_fields()`: Find unextracted fields

#### 2. GeminiClient (AI Core)

Handles all interactions with Gemini API.

```python
from app.services.speech.gemini_client import GeminiClient

client = GeminiClient()

# Speech-to-Text
transcript, confidence = client.transcribe_audio(audio_bytes)

# Product attribute extraction (returns dict + confidences)
attributes, field_confidences = client.extract_product_attributes(text)

# English normalization
normalized, confidence = client.normalize_to_english(text, source_lang)
```

**Features**:
- Uses `google-genai>=2.22.0` SDK (official Python client)
- Graceful error handling with sensible defaults
- No API key exposure in logs
- Per-field confidence scoring for extracted attributes

#### 3. AudioProcessor

Handles audio file validation.

```python
from app.services.speech.audio_processor import AudioProcessor

# Validate path exists and format is supported
valid = AudioProcessor.validate_audio_path(storage_path, storage_root)

# Get file size
size = AudioProcessor.get_audio_size(storage_path, storage_root)

# Read raw audio bytes for Gemini
audio_bytes = AudioProcessor.read_audio_bytes(storage_path, storage_root)
```

**Supported Formats**: .wav, .mp3, .flac, .ogg

#### 4. LanguageDetector

Detects language from text.

```python
from app.services.speech.language_detection import LanguageDetector

lang_code, confidence = LanguageDetector.detect(text)
# Returns: ("en", 0.85), ("kn", 0.92), etc.
```

**Supported Languages**:
- `en` - English
- `kn` - Kannada
- `hi` - Hindi
- `ta` - Tamil
- `te` - Telugu
- `ml` - Malayalam

**Detection Method**:
- Unicode character range detection (high confidence: 0.9)
- Common word detection (medium confidence: 0.5-0.7)
- Fallback to English for undetected scripts

#### 5. Legacy Components (Backward Compatibility)

For testing and legacy support:

- **Translator** - Translation placeholder (real work done by GeminiClient)
- **ProductInfoExtractor** - Rule-based extraction fallback

## Environment Configuration

### Required for Gemini Integration

```bash
# API Keys (at least one required)
GEMINI_SPEECH_KEY=your_api_key      # For speech-to-text
GEMINI_CATALOG_KEY=your_api_key     # For product extraction

# Model names (optional, defaults provided)
GEMINI_SPEECH_MODEL=gemini-2.0-flash
GEMINI_CATALOG_MODEL=gemini-2.0-flash

# Storage
STORAGE_ROOT=data/uploads
```

### Backward Compatibility

The module maintains backward compatibility:
- `transcript` parameter allows pre-transcribed text (bypasses Gemini STT)
- Legacy extraction methods still available for testing
- All tests pass with both Gemini and fallback implementations

## Usage Example

```python
from app.services.speech import VoiceProcessor

# Initialize
processor = VoiceProcessor(storage_root="data/uploads")

# Prepare input
input_data = {
    "product_id": "ART-001",
    "audio": {
        "audio_id": "audio_001",
        "storage_path": "products/ART-001/audio_001.wav"
    }
}

# Production: Real audio transcription
# result = processor.process_from_input(input_data)

# Development: With transcript override for testing
transcript = "I make beautiful handmade silk scarves 180 cm long and red in color"
result = processor.process_from_input(input_data, transcript=transcript)

# Access results
print(result.product.name)           # Extracted product name
print(result.voice.language_code)    # Detected language
print(result.missing_fields)         # Fields not mentioned
print(result.field_confidence)       # Confidence scores per field
print(result.to_dict())              # Full schema-compliant output
```

## Data Flow

### Step-by-Step Processing

1. **Validate Audio**: Check file exists and format is supported
2. **Transcribe**: Send audio to Gemini for speech-to-text
3. **Detect Language**: Identify language from transcript
4. **Normalize**: If non-English, use Gemini to translate to English
5. **Extract**: Use Gemini to extract product attributes with confidence scores
6. **Identify Missing**: Compare extracted fields to schema
7. **Return**: Build VoiceProcessingResult with all metadata

### Confidence Scoring

Each extraction step contributes confidence:
- **speech_to_text**: How well Gemini heard/transcribed the audio (0.0-1.0)
- **language_detection**: How certain about the detected language (0.0-1.0)
- **normalization**: Quality of English normalization if performed (0.0-1.0)
- **Per-field**: Gemini's confidence in each extracted attribute (0.0-1.0)

## Important Principles

### No Hallucination

**CRITICAL**: The module only extracts information explicitly mentioned in the transcript.

- If the artisan doesn't mention weight → `weight.value = None`
- If the artisan doesn't mention category → `category = null`
- If the artisan doesn't mention special features → `special_features = []`

**Never** estimate, guess, or invent missing information.

### Gemini Integration Notes

- Uses official `google-genai` library (v2.22.0+)
- Sends audio as binary to Gemini's Speech-to-Text model
- Extracts attributes via JSON-mode structured output
- Handles API failures gracefully with fallback logic
- All API calls include error logging and retry logic

## Testing

Run the comprehensive test suite:

```bash
python -m pytest tests/test_voice_processor.py -v
```

**Test Coverage**:
- Language detection (5 tests)
- Translation/normalization (4 tests)
- Product information extraction (9 tests)
- Complete voice processing (7 tests)
- Schema compliance (1 test)
- Edge cases (4 tests)

**Total: 30 tests passing**

### Test Strategy

Tests use mock/override mechanisms:
- `transcript` parameter allows testing without real audio files
- Gemini API failures are handled gracefully
- Backward compatibility with legacy extraction methods tested
- Unicode and special character handling verified

## Integration with Other Modules

### Photo Intelligence (Vision Module)

The voice module output provides:
- Product name and category for media tagging
- Craft type for image categorization
- Dimensions for aspect ratio matching
- Material information for texture matching

### Pricing Intelligence Module

The voice module provides:
- Material type (for cost calculation)
- Production time (for labour cost)
- Craft type (for market segmentation)
- Category/subcategory (for pricing benchmarks)

### Catalogue Module

The voice module provides:
- Complete product description
- Structured attributes for filtering
- Missing fields indicating gaps
- Confidence scores for review workflows

## Error Handling

### Audio File Not Found

```python
# Logged as warning, processing continues gracefully
result.voice.original_transcript = None
result.voice.confidence = 0.0
# All product fields remain null
```

### Invalid API Configuration

```python
# If GEMINI_SPEECH_KEY not set, falls back to transcript parameter
logger.warning("No Gemini API key configured")
# Can still process with provided transcript
```

### Missing Required Fields

```python
# Raises ValueError with clear message
processor.process_from_input({"product_id": "ART-001"})
# ValueError: "Missing required fields: audio.audio_id, audio.storage_path"
```

### Empty Transcript

```python
# Gracefully handles null transcript
result = processor.process(..., transcript=None)
# Returns valid result with null product fields
# missing_fields contains all fields
```

## Performance Considerations

- **Text Processing**: Sub-second for typical transcripts (<1000 words)
- **Gemini API Calls**: ~2-5 seconds (transcription + extraction)
- **Memory**: Minimal base usage, scales with audio file size
- **Storage I/O**: Efficient file validation without full reads

## Troubleshooting

### "No Gemini API key configured"

**Fix**: Set environment variables:
```bash
export GEMINI_SPEECH_KEY=your_key
export GEMINI_CATALOG_KEY=your_key
```

### Extraction results are empty

**Check**:
1. Transcript contains relevant product information
2. Language is detected correctly
3. Audio quality is sufficient for transcription
4. Gemini model has been selected properly

### Low confidence scores

**Causes**:
- Unclear audio quality
- Mixed languages in transcript
- Non-standard terminology
- Rapid or unclear speech

## Future Enhancements

1. **NLP Model Integration**
   - Named entity recognition for attributes
   - Semantic similarity for better categorization
   - Dependency parsing for relationship extraction

2. **Multi-Language Support**
   - Real-time code-switching detection
   - Per-language model optimization
   - Transliteration support

3. **Quality Assurance Pipeline**
   - Low-confidence automatic review workflows
   - Human feedback integration
   - Model fine-tuning on feedback

## Support and Maintenance

For questions or issues:
- Check test cases: `tests/test_voice_processor.py`
- Review implementation: `app/services/speech/`
- Inspect Gemini integration: `app/services/speech/gemini_client.py`
- Check configuration: `.env` and `requirements.txt`

## Schema Compliance

This module produces output compliant with the shared product intelligence schema. All output values follow strict rules:
- Actual extracted values when reliably available
- `null` only when genuinely unavailable (never estimated)
- `[]` only when there are genuinely no items
- Confidence scores indicate extraction reliability
