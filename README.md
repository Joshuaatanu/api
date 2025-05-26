# Enhanced English-Igala Translation API 🌍

A comprehensive Flask-based API for English-Igala translation with advanced features including batch processing, confidence scoring, translation history, and user analytics.

## 🚀 Features

### Core Translation
- ✅ **Single Translation** - Translate individual texts with confidence scores
- ✅ **Batch Translation** - Process multiple texts simultaneously
- ✅ **Bidirectional Translation** - Support both English→Igala and Igala→English
- ✅ **Translation Confidence Scores** - Reliability metrics for each translation
- ✅ **Language Auto-detection** - Automatically detect input language

### Dictionary & Learning
- ✅ **Word Suggestions** - Autocomplete functionality for both languages
- ✅ **POS Tagging** - Part-of-speech analysis for linguistic insights
- ✅ **Synthetic Data Generation** - Create training data for model improvement

### User Features
- ✅ **Translation History** - Persistent storage of user translations
- ✅ **Favorites Management** - Save and organize favorite translations
- ✅ **User Analytics** - Comprehensive usage statistics and insights
- ✅ **Data Export** - Export user data in JSON or Excel format

### Utility & Admin
- ✅ **API Health Monitoring** - System status and health checks
- ✅ **CSV Processing** - Bulk processing of translation data
- ✅ **Error Logging** - Comprehensive error handling and reporting

## 📋 Requirements

- Python 3.7+
- Flask
- pandas
- nltk
- sqlite3
- openpyxl

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd backend/api
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data:**
```python
import nltk
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger_eng')
```

## 🚀 Quick Start

1. **Start the server:**
```bash
python main.py
```

2. **Test the API:**
```bash
python test_api.py
```

3. **Access the API:**
- Base URL: `http://localhost:10000`
- Health Check: `http://localhost:10000/health`

## 📖 API Usage Examples

### Single Translation
```python
import requests

response = requests.post('http://localhost:10000/translate', json={
    'english-text': 'Good morning',
    'direction': 'en_to_ig',
    'user_id': 'user123'
})

result = response.json()
print(f"Translation: {result['translated']}")
print(f"Confidence: {result['confidence']}%")
```

### Batch Translation
```python
response = requests.post('http://localhost:10000/translate/batch', json={
    'texts': ['Hello', 'Thank you', 'Goodbye'],
    'direction': 'en_to_ig',
    'user_id': 'user123'
})

results = response.json()
print(f"Average confidence: {results['average_confidence']}%")
for result in results['results']:
    print(f"{result['original']} → {result['translated']}")
```

### Language Detection
```python
response = requests.post('http://localhost:10000/detect-language', json={
    'text': 'Sannu lafiya'
})

result = response.json()
print(f"Detected language: {result['detected_language']}")
```

### Word Suggestions
```python
response = requests.post('http://localhost:10000/suggestions', json={
    'partial_word': 'hel',
    'language': 'english',
    'limit': 5
})

suggestions = response.json()['suggestions']
print(f"Suggestions: {suggestions}")
```

## 📊 Analytics & Insights

### User Analytics
```python
response = requests.get('http://localhost:10000/analytics/user123')
analytics = response.json()

print(f"Total translations: {analytics['total_translations']}")
print(f"Average confidence: {analytics['average_confidence']}%")
print(f"Direction stats: {analytics['direction_stats']}")
```

### Translation History
```python
response = requests.get('http://localhost:10000/history/user123?limit=10')
history = response.json()

for translation in history['history']:
    print(f"{translation['original_text']} → {translation['translated_text']}")
```

## 🗂️ Data Management

### Export User Data
```python
# JSON export
response = requests.get('http://localhost:10000/export/user123?format=json')
data = response.json()

# Excel export
response = requests.get('http://localhost:10000/export/user123?format=csv')
# Downloads Excel file with translations and favorites
```

### Favorites Management
```python
# Add to favorites
requests.post('http://localhost:10000/favorites', json={
    'user_id': 'user123',
    'original_text': 'Hello',
    'translated_text': 'Sannu',
    'direction': 'en_to_ig'
})

# Get favorites
response = requests.get('http://localhost:10000/favorites/user123')
favorites = response.json()['favorites']
```

## 🏗️ Project Structure

```
backend/api/
├── main.py                 # Main Flask application
├── model.py               # Enhanced translation model
├── requirements.txt       # Python dependencies
├── test_api.py           # Comprehensive test suite
├── API_DOCUMENTATION.md  # Detailed API documentation
├── README.md             # This file
├── clean_2.csv           # Translation data
├── translation_history.db # SQLite database (auto-created)
└── nltk/                 # NLTK data directory
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for configuration:
```env
PORT=10000
DEBUG=True
DATABASE_URL=sqlite:///translation_history.db
```

### Database Schema
The API automatically creates SQLite tables:
- `translations` - Translation history
- `favorites` - User favorites

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

The test suite covers:
- Health checks
- Single and batch translation
- Language detection
- Word suggestions
- POS analysis
- Favorites management
- Translation history
- User analytics
- Data export

## 📈 Performance Metrics

The API tracks:
- Translation accuracy (confidence scores)
- Response times
- User engagement metrics
- Error rates
- Database performance

## 🔮 Future Enhancements

### Planned Features
- **WebSocket Support** - Real-time translation
- **Voice Integration** - Speech-to-text and text-to-speech
- **OCR Capabilities** - Image text extraction
- **Advanced NLP** - Sentiment analysis, summarization
- **Mobile Support** - Offline translation models
- **Multi-language** - Support for additional language pairs

### Advanced Features (Roadmap)
- **User Authentication** - Secure login/signup system
- **Rate Limiting** - API usage controls
- **Caching** - Redis-based response caching
- **Monitoring** - Prometheus metrics and Grafana dashboards
- **Containerization** - Docker deployment
- **Cloud Integration** - AWS/GCP deployment options

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or feature requests:
1. Check the API documentation
2. Run the test suite to identify issues
3. Create an issue in the repository
4. Contact the development team

## 🙏 Acknowledgments

- NLTK team for natural language processing tools
- Flask community for the web framework
- Contributors to the Igala language preservation effort

---

**Ready to translate? Start your server and explore the enhanced API!** 🚀 