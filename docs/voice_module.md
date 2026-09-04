"""Voice & Language Intelligence Module Documentation

## Overview

The Voice & Language Intelligence module enables artisans to describe their products through natural speech in their native language. The module handles the complete pipeline from audio input to structured product information.

## Module Responsibility

**Owner**: Voice & Language Intelligence team  
**Location**: `app/services/speech/`  
**Primary Function**: Convert artisan voice input → structured product information

## Pipeline

```
ARTISAN SPEECH
    ↓
AUDIO FILE (stored)
    ↓
SPEECH-TO-TEXT
    ↓
ORIGINAL TRANSCRIPT
    ↓
LANGUAGE DETECTION
    ↓
TRANSLATION (to English)
    ↓
PRODUCT INFO EXTRACTION
    ↓
MISSING FIELD IDENTIFICATION
    ↓
CONFIDENCE SCORING
    ↓
STRUCTURED JSON (schema-compliant)
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

**Important**: The module reads audio from the file system (see `AudioProcessor.validate_audio_path()`). The path is relative to `STORAGE_ROOT` configured in environment settings.

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
    "translation": "0.0 to 1.0",
    "overall": "0.0 to 1.0"
  }
}
```

## Core Components

### 1. VoiceProcessor

Main orchestrator for the entire pipeline.

```python
processor = VoiceProcessor(storage_root="data/uploads")
result = processor.process_from_input(input_data, transcript="optional transcript")
```

**Methods**:
- `process()`: Process with product_id, audio_id, storage_path, and optional transcript
- `process_from_input()`: Process using standard input dictionary format
- `to_dict()`: Convert result to JSON-serializable dictionary

### 2. LanguageDetector

Detects the language spoken in the transcript.

```python
lang_code, confidence = LanguageDetector.detect(text)
# Returns: ("en", 0.85) or ("kn", 0.92) etc.
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

### 3. Translator

Handles translation from detected language to English (canonical processing language).

```python
translated_text, confidence = Translator.translate(original_text, source_lang)
```

**Current MVP Implementation**:
- English text: No translation (confidence: 1.0)
- Non-English: Returns placeholder with lower confidence (0.4)
- **Production**: Should integrate with Google Translate API

### 4. ProductInfoExtractor

Extracts structured fields from transcript text.

```python
product = ProductInfoExtractor.extract_all(transcript)
missing_fields = ProductInfoExtractor.get_missing_fields(product)
```

**Extraction Method**:
- Keyword and pattern matching
- Regex-based dimension/weight parsing
- Special feature identification
- Missing field tracking

**Supported Fields**:
- Basic: name, category, subcategory, material, color, craft_type
- Dimensions: length, width, height (with units)
- Weight: value and unit
- Special: usage, pattern, production_time, special_features

### 5. AudioProcessor

Handles audio file validation and metadata.

```python
AudioProcessor.validate_audio_path(storage_path, storage_root)
file_size = AudioProcessor.get_audio_size(storage_path, storage_root)
```

**Supported Formats**: .wav, .mp3, .flac, .ogg

## Usage Example

```python
from app.services.speech import VoiceProcessor

# Initialize processor
processor = VoiceProcessor(storage_root="data/uploads")

# Prepare input
input_data = {
    "product_id": "ART-001",
    "audio": {
        "audio_id": "audio_001",
        "storage_path": "products/ART-001/audio_001.wav"
    }
}

# For MVP/testing with transcript
transcript = "I make beautiful handmade silk scarves 180 cm long and red in color"

# Process
result = processor.process_from_input(input_data, transcript)

# Access results
print(result.product.name)  # Extracted product name
print(result.voice.language_code)  # Detected language
print(result.missing_fields)  # Fields not mentioned
print(result.to_dict())  # Full schema-compliant output
```

## Configuration

### Environment Variables

```bash
# Storage configuration
STORAGE_ROOT=data/uploads

# Speech-to-Text (future)
GEMINI_SPEECH_KEY=your_api_key
GEMINI_SPEECH_MODEL=model_name
```

## Important Principles

### No Hallucination

**CRITICAL**: The module only extracts information explicitly mentioned in the transcript.

- If the artisan doesn't mention weight → `weight.value = None`
- If the artisan doesn't mention category → `category = null`
- If the artisan doesn't mention special features → `special_features = []`

**Never** estimate, guess, or invent missing information.

### Confidence Scoring

Confidence scores indicate processing quality at each stage:
- **1.0** = High confidence (verified)
- **0.7-0.9** = Good confidence (likely accurate)
- **0.4-0.7** = Moderate confidence (review recommended)
- **0.0-0.4** = Low confidence (may need manual verification)

### Language Support

The module is designed for Indian languages but extensible to others. Current support:
- Primary: Kannada, Hindi, Tamil, Telugu, Malayalam
- Fallback: English

## MVP vs. Production

### Current MVP Implementation

- **Speech-to-Text**: Requires pre-transcribed text input (for testing)
- **Language Detection**: Pattern-based with Unicode range detection
- **Translation**: Placeholder implementation (logs requirement)
- **Extraction**: Rule-based with regex patterns

### Production Requirements

- **Speech-to-Text**: Integration with Google Cloud Speech-to-Text or similar
- **Language Detection**: Current implementation sufficient
- **Translation**: Integration with Google Translate API
- **Extraction**: Could be enhanced with NLP models (NER, dependency parsing)
- **Storage**: Audio file access layer (cloud storage integration)

## Testing

Run the comprehensive test suite:

```bash
python -m unittest discover -s tests -p "test_voice_processor.py" -v
```

**Test Coverage**:
- Language detection (5 tests)
- Translation pipeline (4 tests)
- Product information extraction (8 tests)
- Complete voice processing (6 tests)
- Schema compliance (1 test)
- Edge cases (6 tests)

**All 30 tests passing**

## Integration with Other Modules

### Media Intelligence (Vision)

The voice module output provides:
- Product name and category for media filtering
- Craft type for image categorization
- Product dimensions for photo orientation detection

### Pricing Intelligence

The voice module provides:
- Material costs (if artisan mentions)
- Production time (for labour calculation)
- Category information for market reference

### Catalogue Generation

The voice module provides:
- Complete product description
- Structured attributes for catalogue display
- Missing fields for content gap analysis

## Error Handling

### File Not Found

If audio file doesn't exist:
```python
# Logged as warning but processing continues
# result.voice.original_transcript = None
```

### Invalid Input

Missing required fields raises `ValueError`:
```python
# Example: missing audio information
try:
    processor.process_from_input({"product_id": "ART-001"})
except ValueError as e:
    print(e)  # "Missing required fields: ..."
```

### Empty Transcript

Graceful handling:
```python
# If transcript is None or empty
result = processor.process(..., transcript=None)
# Returns valid result with null product fields
# product fields remain null
# missing_fields = [all fields]
```

## Performance Considerations

- **Text Processing**: Sub-second for typical transcripts (<1000 words)
- **Regex Extraction**: Fast for pattern-based field extraction
- **Memory**: Minimal (no ML models in current MVP)
- **Storage I/O**: File existence check only (reads file size, not content)

## Future Enhancements

1. **NLP Model Integration**
   - Named entity recognition for product attributes
   - Dependency parsing for relationship extraction
   - Semantic similarity for better material/category detection

2. **Speech Recognition Integration**
   - Real-time speech-to-text processing
   - Multi-speaker support for group descriptions
   - Noise handling and audio preprocessing

3. **Quality Assurance**
   - Confidence threshold enforcement
   - Manual review workflow for low-confidence extractions
   - Feedback loop for model improvement

4. **Extended Language Support**
   - More regional languages
   - Script-specific optimizations
   - Transliteration support

## Support and Maintenance

For questions or issues:
- Check test cases in `tests/test_voice_processor.py`
- Review examples in `app/services/speech/examples.py`
- Check implementation in `app/services/speech/voice_processor.py`

## Schema Compliance

This module produces output compliant with:
- `app/schemas/product_intelligence.json`
- Voice section of the shared product intelligence schema

All output values follow the schema rules:
- Actual values when reliably available
- `null` only when genuinely unavailable (never estimated)
- `[]` only when there are genuinely no items
- `0` only when the actual value is zero
