from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
import nltk
from io import BytesIO
import os
import re
import pandas as pd
from flask_cors import CORS
import random
from model import translate_model, get_model
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import json
from typing import List

# Initialize NLTK resources path
nltk_path = './nltk'
if os.path.exists(os.path.join(nltk_path, 'taggers', 'averaged_perceptron_tagger', 'averaged_perceptron_tagger.pickle')):
    print("Resource found!")
else:
    print("Resource not found!")
    nltk.download('punkt_tab')
    nltk.download('averaged_perceptron_tagger_eng')


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database for translation history
def init_db():
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            original_text TEXT,
            translated_text TEXT,
            direction TEXT,
            confidence REAL,
            timestamp TEXT,
            session_id TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            original_text TEXT,
            translated_text TEXT,
            direction TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Function to get POS tags as a string


def get_pos_tags(english_word):
    tokens = nltk.word_tokenize(english_word)
    tagged_words = nltk.pos_tag(tokens)
    return ', '.join([tag for word, tag in tagged_words])

# Helper function to save translation to history
def save_translation_history(user_id, original, translated, direction, confidence, session_id=None):
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO translations (user_id, original_text, translated_text, direction, confidence, timestamp, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, original, translated, direction, confidence, datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()

# Helper function to get a random word by POS tag


def get_random_word(df, pos_tag):
    words = df[df["POS"].str.contains(pos_tag, na=False)]["Igala"].tolist()
    if words:
        return random.choice(words)
    else:
        return None

# Helper function to get the English translation of an Igala word


def get_english_translation(df, igala_word):
    translation = df[df["Igala"] == igala_word]["English"].tolist()
    if translation:
        return translation[0]
    else:
        return None

# Home route


@app.route('/')
def home():
    return render_template('home.html')

# Contact page route


@app.route("/contact")
def contact():
    return render_template("contact.html")

# Enhanced translate route with confidence scores
@app.route('/translate', methods=['POST', 'GET'])
def translate():
    if request.method == 'POST':
        data = request.json
        text = data.get('english-text', '')
        direction = data.get('direction', 'en_to_ig')  # en_to_ig or ig_to_en
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id')
        
        model = get_model()
        result = model.translate_single(text, direction)
        
        # Save to history
        save_translation_history(
            user_id, 
            result['original'], 
            result['translated'], 
            result['direction'], 
            result['confidence'],
            session_id
        )
        
        return jsonify(result)
    return jsonify(translated_text="")

# New batch translation endpoint
@app.route('/translate/batch', methods=['POST'])
def translate_batch():
    data = request.json
    texts = data.get('texts', [])
    direction = data.get('direction', 'en_to_ig')
    user_id = data.get('user_id', 'anonymous')
    session_id = data.get('session_id')
    
    if not texts or not isinstance(texts, list):
        return jsonify({"error": "Invalid input. Expected list of texts."}), 400
    
    model = get_model()
    results = model.translate_batch(texts, direction)
    
    # Save all translations to history
    for result in results:
        save_translation_history(
            user_id,
            result['original'],
            result['translated'],
            result['direction'],
            result['confidence'],
            session_id
        )
    
    return jsonify({
        "results": results,
        "total_translations": len(results),
        "average_confidence": sum(r['confidence'] for r in results) / len(results) if results else 0
    })

# Language auto-detection endpoint
@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    model = get_model()
    detected_language = model.auto_detect_language(text)
    
    return jsonify({
        "text": text,
        "detected_language": detected_language
    })

# Word suggestions endpoint for autocomplete
@app.route('/suggestions', methods=['POST'])
def get_suggestions():
    data = request.json
    partial_word = data.get('partial_word', '')
    language = data.get('language', 'english')
    limit = data.get('limit', 5)
    
    if not partial_word:
        return jsonify({"suggestions": []})
    
    model = get_model()
    suggestions = model.get_word_suggestions(partial_word, language, limit)
    
    return jsonify({
        "partial_word": partial_word,
        "suggestions": suggestions,
        "language": language
    })

# Translation history endpoints
@app.route('/history/<user_id>', methods=['GET'])
def get_translation_history(user_id):
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM translations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'original_text': row[2],
            'translated_text': row[3],
            'direction': row[4],
            'confidence': row[5],
            'timestamp': row[6],
            'session_id': row[7]
        })
    
    return jsonify({
        "history": history,
        "total": len(history),
        "limit": limit,
        "offset": offset
    })

# Favorites management
@app.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    original_text = data.get('original_text', '')
    translated_text = data.get('translated_text', '')
    direction = data.get('direction', 'en_to_ig')
    
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO favorites (user_id, original_text, translated_text, direction, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, original_text, translated_text, direction, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Added to favorites successfully"})

@app.route('/favorites/<user_id>', methods=['GET'])
def get_favorites(user_id):
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM favorites 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    favorites = []
    for row in rows:
        favorites.append({
            'id': row[0],
            'original_text': row[2],
            'translated_text': row[3],
            'direction': row[4],
            'timestamp': row[5]
        })
    
    return jsonify({"favorites": favorites})

# API health monitoring
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        conn = sqlite3.connect('translation_history.db')
        conn.close()
        
        # Test model loading
        model = get_model()
        test_result = model.translate_single("test", "en_to_ig")
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "model": "loaded",
            "version": "2.0"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# Process CSV route


@app.route('/process_csv', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)

        # Apply the POS tagging function to the 'English' column
        df['POS'] = df['English'].apply(get_pos_tags)

        # Save the updated DataFrame to a CSV file using BytesIO
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)

        # Return the CSV file as a response
        return send_file(output, mimetype='text/csv', download_name='updated_with_pos.csv', as_attachment=True)

    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

# Generate synthetic data route


@app.route('/generate_synthetic_data', methods=['POST'])
def generate_synthetic_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        # Read the uploaded CSV file into a DataFrame
        data = pd.read_csv(file)

        # Retrieve the number of samples from the request body
        num_samples = request.form.get('num_samples', 100, type=int)
        synthetic_data = []

        for _ in range(num_samples):
            adjective = get_random_word(data, r"\bJJ\b")
            noun1 = get_random_word(data, r"\bNN\b")
            verb = get_random_word(data, r"\bVB\b")
            noun2 = get_random_word(data, r"\bNN\b")

            # Ensure we found valid words and apply more logical pairings
            if noun1 and noun2 and adjective and verb:
                if random.choice([True, False]):
                    # Adjective + Noun + Verb + Noun
                    igala_phrase = f"{adjective} {noun1} {verb} {noun2}"
                    english_phrase = f"The {get_english_translation(data, adjective)} {get_english_translation(data, noun1)} {get_english_translation(data, verb)} the {get_english_translation(data, noun2)}"
                else:
                    # Noun + Verb + Noun
                    igala_phrase = f"{noun1} {verb} {noun2}"
                    english_phrase = f"The {get_english_translation(data, noun1)} {get_english_translation(data, verb)} the {get_english_translation(data, noun2)}"

                synthetic_data.append([igala_phrase, english_phrase])

        # Create DataFrame from the generated data
        synthetic_df = pd.DataFrame(
            synthetic_data, columns=["Igala", "English"])

        # Return the generated data as JSON
        return jsonify(synthetic_df.to_dict(orient='records'))

    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400

# Submit translation for POS analysis
@app.route('/submit_translation', methods=['POST'])
def submit_translation():
    try:
        # Get the submitted translation text from the request
        translation_text = request.json.get('translation_text', '')

        if not translation_text:
            return jsonify({"error": "No translation text provided"}), 400

        # Get POS tags for the submitted translation
        pos_tags = get_pos_tags(translation_text)

        # Return the POS tags as a JSON response
        return jsonify({
            "original_text": translation_text,
            "pos_tags": pos_tags
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Analytics endpoint
@app.route('/analytics/<user_id>', methods=['GET'])
def get_user_analytics(user_id):
    conn = sqlite3.connect('translation_history.db')
    cursor = conn.cursor()
    
    # Get translation count by direction
    cursor.execute('''
        SELECT direction, COUNT(*) as count 
        FROM translations 
        WHERE user_id = ? 
        GROUP BY direction
    ''', (user_id,))
    direction_stats = dict(cursor.fetchall())
    
    # Get average confidence
    cursor.execute('''
        SELECT AVG(confidence) as avg_confidence 
        FROM translations 
        WHERE user_id = ?
    ''', (user_id,))
    avg_confidence = cursor.fetchone()[0] or 0
    
    # Get total translations
    cursor.execute('''
        SELECT COUNT(*) as total 
        FROM translations 
        WHERE user_id = ?
    ''', (user_id,))
    total_translations = cursor.fetchone()[0]
    
    # Get recent activity (last 7 days)
    cursor.execute('''
        SELECT DATE(timestamp) as date, COUNT(*) as count 
        FROM translations 
        WHERE user_id = ? AND datetime(timestamp) >= datetime('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (user_id,))
    recent_activity = dict(cursor.fetchall())
    
    conn.close()
    
    return jsonify({
        "user_id": user_id,
        "total_translations": total_translations,
        "average_confidence": round(avg_confidence, 2),
        "direction_stats": direction_stats,
        "recent_activity": recent_activity
    })

# Export user data
@app.route('/export/<user_id>', methods=['GET'])
def export_user_data(user_id):
    format_type = request.args.get('format', 'json')  # json or csv
    
    conn = sqlite3.connect('translation_history.db')
    
    # Get translations
    translations_df = pd.read_sql_query('''
        SELECT original_text, translated_text, direction, confidence, timestamp 
        FROM translations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', conn, params=(user_id,))
    
    # Get favorites
    favorites_df = pd.read_sql_query('''
        SELECT original_text, translated_text, direction, timestamp 
        FROM favorites 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    ''', conn, params=(user_id,))
    
    conn.close()
    
    if format_type == 'csv':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            translations_df.to_excel(writer, sheet_name='Translations', index=False)
            favorites_df.to_excel(writer, sheet_name='Favorites', index=False)
        output.seek(0)
        
        return send_file(
            output, 
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name=f'{user_id}_translation_data.xlsx',
            as_attachment=True
        )
    else:
        return jsonify({
            "user_id": user_id,
            "translations": translations_df.to_dict(orient='records'),
            "favorites": favorites_df.to_dict(orient='records'),
            "export_timestamp": datetime.now().isoformat()
        })

# Back Translation endpoints for quality assessment
@app.route('/back-translate', methods=['POST'])
def back_translate():
    """Perform back translation for quality assessment"""
    try:
        data = request.json
        text = data.get('text', '')
        source_direction = data.get('source_direction', 'en_to_ig')
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        model = get_model()
        result = model.back_translate(text, source_direction)
        
        # Save back translation to history with special marking
        save_translation_history(
            user_id,
            f"[BACK-TRANSLATE] {result['original_text']}",
            f"Forward: {result['forward_translation']} | Back: {result['back_translation']}",
            f"back_{source_direction}",
            result['overall_quality']['overall_score'],
            session_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/back-translate/batch', methods=['POST'])
def batch_back_translate():
    """Perform batch back translation for quality assessment"""
    try:
        data = request.json
        texts = data.get('texts', [])
        source_direction = data.get('source_direction', 'en_to_ig')
        user_id = data.get('user_id', 'anonymous')
        session_id = data.get('session_id')
        
        if not texts or not isinstance(texts, list):
            return jsonify({"error": "Invalid input. Expected list of texts."}), 400
        
        model = get_model()
        result = model.batch_back_translate(texts, source_direction)
        
        # Save all back translations to history
        for back_translation in result['results']:
            save_translation_history(
                user_id,
                f"[BATCH-BACK-TRANSLATE] {back_translation['original_text']}",
                f"Forward: {back_translation['forward_translation']} | Back: {back_translation['back_translation']}",
                f"batch_back_{source_direction}",
                back_translation['overall_quality']['overall_score'],
                session_id
            )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/translation-quality', methods=['POST'])
def assess_translation_quality():
    """Assess translation quality using back translation"""
    try:
        data = request.json
        original_text = data.get('original_text', '')
        translated_text = data.get('translated_text', '')
        direction = data.get('direction', 'en_to_ig')
        
        if not original_text or not translated_text:
            return jsonify({"error": "Both original_text and translated_text are required"}), 400
        
        model = get_model()
        
        # Perform back translation on the provided translation
        back_direction = 'ig_to_en' if direction == 'en_to_ig' else 'en_to_ig'
        back_result = model.translate_single(translated_text, back_direction)
        back_translation = back_result['translated']
        back_confidence = back_result['confidence']
        
        # Calculate quality metrics
        quality_metrics = model.calculate_back_translation_score(original_text, back_translation)
        
        # Assess overall quality (assuming forward confidence of 100% since translation is provided)
        overall_quality = model._assess_translation_quality(100.0, back_confidence, quality_metrics['similarity_score'])
        
        return jsonify({
            'original_text': original_text,
            'provided_translation': translated_text,
            'back_translation': back_translation,
            'back_confidence': back_confidence,
            'quality_metrics': quality_metrics,
            'overall_quality': overall_quality,
            'direction': direction,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/quality-report/<user_id>', methods=['GET'])
def get_quality_report(user_id):
    """Generate a quality report for user's back translations"""
    try:
        conn = sqlite3.connect('translation_history.db')
        cursor = conn.cursor()
        
        # Get back translation history
        cursor.execute('''
            SELECT original_text, translated_text, confidence, timestamp 
            FROM translations 
            WHERE user_id = ? AND direction LIKE 'back_%'
            ORDER BY timestamp DESC
        ''', (user_id,))
        
        back_translations = cursor.fetchall()
        conn.close()
        
        if not back_translations:
            return jsonify({
                "user_id": user_id,
                "message": "No back translation history found",
                "total_back_translations": 0
            })
        
        # Calculate quality statistics
        confidences = [row[2] for row in back_translations]
        avg_quality = sum(confidences) / len(confidences)
        
        quality_distribution = {
            'Excellent (80-100)': sum(1 for c in confidences if c >= 80),
            'Good (60-79)': sum(1 for c in confidences if 60 <= c < 80),
            'Fair (40-59)': sum(1 for c in confidences if 40 <= c < 60),
            'Poor (0-39)': sum(1 for c in confidences if c < 40)
        }
        
        # Recent quality trend (last 10 translations)
        recent_confidences = confidences[:10]
        recent_avg = sum(recent_confidences) / len(recent_confidences) if recent_confidences else 0
        
        return jsonify({
            "user_id": user_id,
            "total_back_translations": len(back_translations),
            "average_quality_score": round(avg_quality, 2),
            "recent_average_quality": round(recent_avg, 2),
            "quality_distribution": quality_distribution,
            "quality_trend": "Improving" if recent_avg > avg_quality else "Stable" if abs(recent_avg - avg_quality) < 5 else "Declining",
            "recommendations": _generate_quality_recommendations(avg_quality, quality_distribution),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _generate_quality_recommendations(avg_quality: float, distribution: dict) -> List[str]:
    """Generate quality improvement recommendations"""
    recommendations = []
    
    if avg_quality < 60:
        recommendations.append("Consider reviewing translation dictionary for better coverage")
        recommendations.append("Focus on improving translations for commonly used words")
    
    if distribution['Poor (0-39)'] > distribution['Excellent (80-100)']:
        recommendations.append("High number of poor quality translations - manual review recommended")
    
    if distribution['Excellent (80-100)'] > 0:
        recommendations.append("Good quality translations detected - continue current approach")
    
    if avg_quality >= 80:
        recommendations.append("Excellent translation quality maintained")
    
    return recommendations

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
