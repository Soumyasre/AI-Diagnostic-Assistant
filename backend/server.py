from flask import Flask, request, jsonify
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from flask_cors import CORS

# Load API credentials
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

# Use a valid Gemini model
model = genai.GenerativeModel('models/gemini-2.0-flash')

app = Flask(__name__)
CORS(app)

@app.route('/generate-response', methods=['POST'])
def generate_response():
    """API to generate follow-up health questions with options."""
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is missing'}), 400

    try:
        prompt = f"""
You are a virtual health assistant.

A user just told you: "{user_message}"

Your task:
1. Generate 3–5 follow-up questions that a doctor might ask.
2. For each question, provide 3–4 multiple choice options.
3. Respond ONLY in this JSON format:

[
  {{
    "question": "Your question here?",
    "options": ["Option A", "Option B", "Option C"]
  }},
  ...
]
"""
        print("here!")
        print()
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("```json").strip("```").strip()

        parsed = json.loads(raw_text)

        questions = [item["question"] for item in parsed]
        options = [item["options"] for item in parsed]

        return jsonify({
            "questions": questions,
            "options": options
        })

    except Exception as e:
        return jsonify({'error': f"Error processing Gemini response: {str(e)}"}), 500

# ✅ NEW DIAGNOSIS ROUTE
@app.route('/generate-diagnosis', methods=['POST'])
def generate_diagnosis():
    """API to generate diagnosis from selected user answers."""
    data = request.get_json()
    user_answers = data.get('answers')  # This should be a list of "Q: ... A: ..." strings

    if not user_answers:
        return jsonify({'error': 'No answers provided'}), 400

    try:
        answers_text = "\n".join(user_answers)

        diagnosis_prompt = f"""
You are a medical diagnostic AI. The user has answered the following questions:

{answers_text}

Based on this input, provide a JSON response with the following structure:
{{
  "symptoms": ["list of inferred symptoms"],
  "diagnosis": "most likely condition",
  "probability": "confidence percentage (e.g., 85%)",
  "suggestions": ["do this", "avoid that"],
  "medications": ["paracetamol", "ibuprofen", ...]
}}

Be concise and informative. Only return valid JSON.
"""

        response = model.generate_content(diagnosis_prompt)
        raw_text = response.text.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.strip("```json").strip("```").strip()

        diagnosis_data = json.loads(raw_text)
        print(diagnosis_data)
        return jsonify(diagnosis_data)

    except Exception as e:
        return jsonify({'error': f"Error generating diagnosis: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
