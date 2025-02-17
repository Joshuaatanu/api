from flask import Flask, render_template, redirect, url_for, request, jsonify, send_file
import nltk
from io import BytesIO
import os
import re
import pandas as pd
from flask_cors import CORS
import random
from model import translate_model

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

# Function to get POS tags as a string


def get_pos_tags(english_word):
    tokens = nltk.word_tokenize(english_word)
    tagged_words = nltk.pos_tag(tokens)
    return ', '.join([tag for word, tag in tagged_words])

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

# Translate route


@app.route('/translate', methods=['POST', 'GET'])
def translate():
    if request.method == 'POST':
        text = request.json['english-text']
        translated_text = translate_model(text)
        return jsonify(translated_text=translated_text)
    return jsonify(translated_text="")

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


# def get_random_word(data, pos, category=None):
#     filtered_words = [
#         row for _, row in data.iterrows() if re.search(pos, row["POS"])
#     ]
#     if category:
#         filtered_words = [
#             row for row in filtered_words if row.get("Category") == category
#         ]  # Accessing using dot notation
#     if filtered_words:
#         # Accessing using brackets
#         return random.choice(filtered_words)["Igala"]
#     return None


# # Updated  `get_english_translation` function (using `.loc` for safer access):

# def get_english_translation(data, igala_word):
#     try:
#         # Safer access
#         return data.loc[data["Igala"] == igala_word, "English"].iloc[0]
#     except IndexError:
#         return None


# @app.route('/generate_synthetic_data', methods=['POST'])
# def generate_synthetic_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        try:  # Handle CSV reading errors
            data = pd.read_csv(file)
        except pd.errors.ParserError as e:  # Be specific about the error type
            return jsonify({"error": f"CSV parsing error: {e}"}), 400
        except Exception as e:  # Catch any other exceptions
            return jsonify({"error": f"Error reading CSV: {e}"}), 500

        # Categorize your data here (This is a simplified example, expand as needed)
        data["Category"] = None
        for index, row in data.iterrows():
            igala_word = row["Igala"]
            if igala_word in ["òkwúta", "únyí", "ítébùlù"]:  # Example objects
                data.loc[index, "Category"] = "object"
            elif igala_word in ["gbà", "du", "jẹ", "kà", "kọ́"]:  # Example actions/verbs
                data.loc[index, "Category"] = "action"
            elif igala_word in ["éfufu", "édúdú", "ékpikpa"]:  # Example colors
                data.loc[index, "Category"] = "color"
            # ... (add more categories as needed. This is crucial for meaningful sentences)

        num_samples = request.form.get('num_samples', 100, type=int)
        synthetic_data = []

        for _ in range(num_samples):
            noun1 = get_random_word(data, r"\bNN\b", "object")
            verb = get_random_word(data, r"\bVB\b", "action")
            noun2 = get_random_word(data, r"\bNN\b", "object")
            adjective = get_random_word(data, r"\bJJ\b", "color")

            if noun1 and verb and noun2:  # Check if crucial elements found
                sentence_structure = random.choice([1, 2])

                if sentence_structure == 1 and adjective:
                    igala_phrase = f"{adjective} {noun1} {verb} {noun2}"
                    english_phrase = f"The {get_english_translation(data, adjective)} {get_english_translation(data, noun1)} {get_english_translation(data, verb)} the {get_english_translation(data, noun2)}"

                elif sentence_structure == 2:  # Skip if no adjective for structure 1
                    igala_phrase = f"{noun1} {verb} {noun2}"
                    english_phrase = f"The {get_english_translation(data, noun1)} {get_english_translation(data, verb)} the {get_english_translation(data, noun2)}"
                else:  # Continue to next iteration if essential components missing
                    continue

                synthetic_data.append([igala_phrase, english_phrase])

        synthetic_df = pd.DataFrame(
            synthetic_data, columns=["Igala", "English"])
        return jsonify(synthetic_df.to_dict(orient='records'))

    return jsonify({"error": "Invalid file format. Please upload a CSV file."}), 400


def submit_translation():
    try:
        # Get the submitted translation text from the request
        translation_text = request.json.get('translation_text', '')

        if not translation_text:
            return jsonify({"error": "No translation text provided"}), 400

        # Use your translation model or logic if necessary
        # translated_text = translate_model(translation_text)  # Uncomment if translation is required

        # Get POS tags for the submitted translation
        pos_tags = get_pos_tags(translation_text)

        # Return the POS tags as a JSON response
        return jsonify({
            "original_text": translation_text,
            "pos_tags": pos_tags
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
