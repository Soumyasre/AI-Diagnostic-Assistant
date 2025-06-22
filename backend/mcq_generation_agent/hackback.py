from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
from flask_cors import CORS


# Load API credentials
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

# Use a valid model
model = genai.GenerativeModel('gemini-2.0-flash')

app = Flask(__name__)
CORS(app)

# from flask import Flask, request, jsonify
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# # Load API credentials
# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not found in .env file")
# genai.configure(api_key=GEMINI_API_KEY)

# # Use a valid Gemini model
# model = genai.GenerativeModel('models/gemini-1.5-pro')

# app = Flask(__name__)

@app.route('/generate-response', methods=['POST'])
def generate_response():
    """API to generate follow-up health questions with options."""
    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'Message is missing'}), 400

    try:
        # Build the prompt
        prompt = f"""
You are a virtual health assistant.

A user just told you: "{user_message}"

Your task is:
1. Generate 3–5 follow-up questions that a doctor might ask to understand the health issue better.
2. For each question, provide 3–4 multiple choice options.
3. Respond in this JSON format:

[
  {{
    "question": "What is your current body temperature?",
    "options": ["Below 98°F", "98–100°F", "Above 100°F"]
  }},
  ...
]
"""

        response = model.generate_content(prompt)
        structured_output = response.text.strip()

    except Exception as e:
        return jsonify({'error': f"Error using Gemini API: {str(e)}"}), 500

    return jsonify({'questions': structured_output})

if __name__ == '__main__':
    app.run(debug=True)
