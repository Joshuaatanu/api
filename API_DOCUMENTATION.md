# English-Igala Translation API Documentation

## Overview
This API provides comprehensive English-Igala translation services with advanced features including batch translation, confidence scoring, translation history, user analytics, and **back translation for quality assessment**.

## Base URL
```
http://localhost:10000
```

## Authentication
Currently, the API uses a simple user_id system. In production, implement proper authentication.

## Core Translation Endpoints

### 1. Single Translation
**POST** `/translate`

Translate a single text with confidence scoring and automatic history saving.

**Request Body:**
```json
{
  "english-text": "Hello world",
  "direction": "en_to_ig",  // "en_to_ig" or "ig_to_en"
  "user_id": "user123",
  "session_id": "session_abc"  // optional
}
```

**Response:**
```json
{
  "original": "Hello world",
  "translated": "Sannu duniya",
  "confidence": 85.5,
  "direction": "en_to_ig",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. Batch Translation
**POST** `/translate/batch`

Translate multiple texts at once with aggregate statistics.

**Request Body:**
```json
{
  "texts": ["Hello", "Good morning", "Thank you"],
  "direction": "en_to_ig",
  "user_id": "user123",
  "session_id": "session_abc"
}
```

**Response:**
```json
{
  "results": [
    {
      "original": "Hello",
      "translated": "Sannu",
      "confidence": 95.0,
      "direction": "en_to_ig",
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "total_translations": 3,
  "average_confidence": 88.3
}
```

## Back Translation & Quality Assessment

### 3. Back Translation
**POST** `/back-translate`

Perform back translation for quality assessment through round-trip translation.

**Request Body:**
```json
{
  "text": "Hello world",
  "source_direction": "en_to_ig",  // "en_to_ig" or "ig_to_en"
  "user_id": "user123",
  "session_id": "session_abc"
}
```

**Response:**
```json
{
  "original_text": "Hello world",
  "forward_translation": "náàgò àná",
  "back_translation": "hello world",
  "forward_confidence": 100.0,
  "back_confidence": 100.0,
  "quality_metrics": {
    "similarity_score": 100.0,
    "word_overlap": 2,
    "total_original_words": 2,
    "preservation_rate": 100.0,
    "overlapping_words": ["hello", "world"]
  },
  "overall_quality": {
    "overall_score": 100.0,
    "quality_level": "Excellent",
    "quality_description": "High-quality translation with good preservation of meaning",
    "recommendations": ["Translation quality is good - no immediate concerns"]
  },
  "source_direction": "en_to_ig",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 4. Batch Back Translation
**POST** `/back-translate/batch`

Perform back translation on multiple texts with quality statistics.

**Request Body:**
```json
{
  "texts": ["Hello", "Good morning", "Thank you"],
  "source_direction": "en_to_ig",
  "user_id": "user123",
  "session_id": "session_abc"
}
```

**Response:**
```json
{
  "results": [
    {
      "original_text": "Hello",
      "forward_translation": "náàgò",
      "back_translation": "hello",
      "forward_confidence": 100.0,
      "back_confidence": 100.0,
      "quality_metrics": {
        "similarity_score": 100.0,
        "word_overlap": 1,
        "total_original_words": 1,
        "preservation_rate": 100.0
      },
      "overall_quality": {
        "overall_score": 100.0,
        "quality_level": "Excellent"
      }
    }
  ],
  "summary": {
    "total_texts": 3,
    "average_quality_score": 95.5,
    "quality_distribution": {
      "Excellent": 2,
      "Good": 1,
      "Fair": 0,
      "Poor": 0
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

### 5. Translation Quality Assessment
**POST** `/translation-quality`

Assess the quality of a provided translation using back translation.

**Request Body:**
```json
{
  "original_text": "Hello world",
  "translated_text": "náàgò àná",
  "direction": "en_to_ig"
}
```

**Response:**
```json
{
  "original_text": "Hello world",
  "provided_translation": "náàgò àná",
  "back_translation": "hello world",
  "back_confidence": 100.0,
  "quality_metrics": {
    "similarity_score": 100.0,
    "word_overlap": 2,
    "total_original_words": 2,
    "preservation_rate": 100.0
  },
  "overall_quality": {
    "overall_score": 100.0,
    "quality_level": "Excellent",
    "quality_description": "High-quality translation with good preservation of meaning"
  },
  "direction": "en_to_ig",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 6. Quality Report
**GET** `/quality-report/{user_id}`

Generate a comprehensive quality report for user's back translations.

**Response:**
```json
{
  "user_id": "user123",
  "total_back_translations": 25,
  "average_quality_score": 87.5,
  "recent_average_quality": 92.0,
  "quality_distribution": {
    "Excellent (80-100)": 15,
    "Good (60-79)": 8,
    "Fair (40-59)": 2,
    "Poor (0-39)": 0
  },
  "quality_trend": "Improving",
  "recommendations": [
    "Good quality translations detected - continue current approach",
    "Excellent translation quality maintained"
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

### 7. Language Detection
**POST** `/detect-language`

Automatically detect if input text is English or Igala.

**Request Body:**
```json
{
  "text": "Sannu lafiya"
}
```

**Response:**
```json
{
  "text": "Sannu lafiya",
  "detected_language": "igala"
}
```

## Dictionary & Learning Features

### 8. Word Suggestions
**POST** `/suggestions`

Get autocomplete suggestions for partial words.

**Request Body:**
```json
{
  "partial_word": "hel",
  "language": "english",  // "english" or "igala"
  "limit": 5
}
```

**Response:**
```json
{
  "partial_word": "hel",
  "suggestions": ["hello", "help", "health", "heart", "heavy"],
  "language": "english"
}
```

### 9. POS Analysis
**POST** `/submit_translation`

Get Part-of-Speech tags for text analysis.

**Request Body:**
```json
{
  "translation_text": "The quick brown fox"
}
```

**Response:**
```json
{
  "original_text": "The quick brown fox",
  "pos_tags": "DT, JJ, JJ, NN"
}
```

## User Features

### 10. Translation History
**GET** `/history/{user_id}`

Retrieve user's translation history with pagination.

**Query Parameters:**
- `limit`: Number of results (default: 50)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "history": [
    {
      "id": 1,
      "original_text": "Hello",
      "translated_text": "Sannu",
      "direction": "en_to_ig",
      "confidence": 95.0,
      "timestamp": "2024-01-15T10:30:00",
      "session_id": "session_abc"
    }
  ],
  "total": 25,
  "limit": 50,
  "offset": 0
}
```

### 11. Favorites Management

#### Add to Favorites
**POST** `/favorites`

**Request Body:**
```json
{
  "user_id": "user123",
  "original_text": "Hello",
  "translated_text": "Sannu",
  "direction": "en_to_ig"
}
```

#### Get Favorites
**GET** `/favorites/{user_id}`

**Response:**
```json
{
  "favorites": [
    {
      "id": 1,
      "original_text": "Hello",
      "translated_text": "Sannu",
      "direction": "en_to_ig",
      "timestamp": "2024-01-15T10:30:00"
    }
  ]
}
```

## Analytics & Insights

### 12. User Analytics
**GET** `/analytics/{user_id}`

Get comprehensive usage statistics for a user.

**Response:**
```json
{
  "user_id": "user123",
  "total_translations": 150,
  "average_confidence": 87.5,
  "direction_stats": {
    "en_to_ig": 120,
    "ig_to_en": 30
  },
  "recent_activity": {
    "2024-01-15": 10,
    "2024-01-14": 8,
    "2024-01-13": 12
  }
}
```

### 13. Data Export
**GET** `/export/{user_id}`

Export user data in JSON or Excel format.

**Query Parameters:**
- `format`: "json" or "csv" (default: "json")

**Response:**
- JSON: Complete data structure
- CSV: Excel file download with separate sheets for translations and favorites

## Utility Endpoints

### 14. Health Check
**GET** `/health`

Check API health and system status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected",
  "model": "loaded",
  "version": "2.0"
}
```

### 15. CSV Processing
**POST** `/process_csv`

Upload CSV file to add POS tags to English words.

**Form Data:**
- `file`: CSV file with English and Igala columns

**Response:** CSV file download with added POS column

### 16. Synthetic Data Generation
**POST** `/generate_synthetic_data`

Generate synthetic translation pairs for training data.

**Form Data:**
- `file`: CSV file with translation data
- `num_samples`: Number of synthetic samples to generate

**Response:**
```json
[
  {
    "Igala": "éfufu òkwúta gbà ítébùlù",
    "English": "The white stone hits the table"
  }
]
```

## Back Translation Quality Metrics

### Quality Levels
- **Excellent (80-100%)**: High-quality translation with good preservation of meaning
- **Good (60-79%)**: Acceptable translation with minor meaning loss
- **Fair (40-59%)**: Translation may have some meaning distortion
- **Poor (0-39%)**: Translation quality is low, manual review recommended

### Quality Metrics Explained
- **Similarity Score**: Percentage of word overlap between original and back-translated text
- **Word Overlap**: Number of words that appear in both original and back-translated text
- **Preservation Rate**: Percentage of original words preserved in back translation
- **Overall Score**: Weighted average of forward confidence, back confidence, and similarity

### Quality Assessment Formula
```
Overall Score = (Forward Confidence × 0.4) + (Back Confidence × 0.3) + (Similarity Score × 0.3)
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

Error responses include descriptive messages:
```json
{
  "error": "No translation text provided"
}
```

## Rate Limiting
Currently not implemented. Consider adding rate limiting for production use.

## Usage Examples

### Python Client Example
```python
import requests

# Single translation
response = requests.post('http://localhost:10000/translate', json={
    'english-text': 'Good morning',
    'direction': 'en_to_ig',
    'user_id': 'user123'
})
result = response.json()
print(f"Translation: {result['translated']}")
print(f"Confidence: {result['confidence']}%")

# Back translation for quality assessment
response = requests.post('http://localhost:10000/back-translate', json={
    'text': 'Good morning',
    'source_direction': 'en_to_ig',
    'user_id': 'user123'
})
result = response.json()
print(f"Original: {result['original_text']}")
print(f"Forward: {result['forward_translation']}")
print(f"Back: {result['back_translation']}")
print(f"Quality: {result['overall_quality']['quality_level']} ({result['overall_quality']['overall_score']}%)")

# Batch back translation
response = requests.post('http://localhost:10000/back-translate/batch', json={
    'texts': ['Hello', 'Thank you', 'Goodbye'],
    'source_direction': 'en_to_ig',
    'user_id': 'user123'
})
results = response.json()
print(f"Average quality: {results['summary']['average_quality_score']}%")
```

### JavaScript Client Example
```javascript
// Back translation
const backTranslate = async (text) => {
  const response = await fetch('/back-translate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      'text': text,
      'source_direction': 'en_to_ig',
      'user_id': 'user123'
    })
  });
  
  const result = await response.json();
  console.log(`Quality: ${result.overall_quality.quality_level}`);
  console.log(`Similarity: ${result.quality_metrics.similarity_score}%`);
  return result;
};

// Quality assessment
const assessQuality = async (original, translation) => {
  const response = await fetch('/translation-quality', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      'original_text': original,
      'translated_text': translation,
      'direction': 'en_to_ig'
    })
  });
  
  const result = await response.json();
  return result.overall_quality;
};
```

## Future Enhancements

Planned features for future versions:
- **Advanced Quality Metrics**: BLEU score, semantic similarity
- **Machine Learning Quality Models**: AI-powered quality assessment
- **Real-time Quality Monitoring**: Live quality dashboards
- **Quality-based Routing**: Automatic fallback for low-quality translations
- **Comparative Analysis**: Quality comparison across different translation approaches
- **Quality Improvement Suggestions**: AI-powered recommendations for better translations

## Support

For issues or questions, please refer to the project repository or contact the development team. 