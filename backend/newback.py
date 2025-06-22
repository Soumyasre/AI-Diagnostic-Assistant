from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import google.generativeai as genai
from datetime import datetime, timezone
from flask_cors import CORS 

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_history.db'
db = SQLAlchemy(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    iq_score = db.Column(db.String(120), nullable=True)  # Added this line

with app.app_context():
    db.create_all()



def check_user_login(user_id, password):
    user = User.query.filter_by(user_id=user_id, password=password).first()
    return user is not None

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200  # Respond to preflight

    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if check_user_login(user_id, password):
        user = User.query.filter_by(user_id=user_id).first()
        return jsonify({
            "message": "Login successful",
            "iq_score": user.iq_score}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
    
@app.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200  # Respond to preflight request

    data = request.get_json()
    user_id = data.get('user_id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"message": "Missing user_id or password"}), 400

    # Check if user already exists
    if User.query.filter_by(user_id=user_id).first():
        return jsonify({"message": "User already exists"}), 409

    # Create new user
    new_user = User(user_id=user_id, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/save-score', methods=['POST'])
def save_score():
    data = request.get_json()
    user_id = data.get('user_id')
    iqscore = data.get('iqscore')

    if not user_id or iqscore is None:
        return jsonify({"error": "Missing user_id or iqscore"}), 400

    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.iq_score = iqscore
    db.session.commit()

    return jsonify({"message": "IQ score saved successfully!"}), 200




class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Chat(user='{self.user_message[:20]}...', bot='{self.bot_response[:20]}...')>"

with app.app_context():
    db.create_all()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

@app.route('/chat', methods=['POST'])

def chat():
    data = request.get_json()
    user_message = data.get('message')
    user_id = data.get('user_id')
    print("hello")
    if not user_message or not user_id:
        return jsonify({'error': 'Message or user_id missing'}), 400
    
    user = User.query.filter_by(user_id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    iq_score = user.iq_score
    if iq_score is None:
        system_instruction = (
            "You are a Python instructor. The user hasn't provided their IQ yet. "
            "Iq is 80,now you can start teaching and remember to be polite."
        )
    else:
        iq_score = int(iq_score)
        if iq_score < 90:
            system_instruction = (
                "You are a Python instructor teaching a beginner with a lower IQ. "
                "Use very simple explanations, repeat concepts, and give lots of easy examples."
            )
        elif iq_score < 120:
            system_instruction = (
                "You are a Python instructor teaching an average IQ student. "
                "Explain concepts clearly with moderate examples and quiz them occasionally."
            )
        else:
            system_instruction = (
                "You are a Python instructor teaching a high IQ student. "
                "Go deep into Python topics, minimize basic explanations, and encourage challenging questions."
            )

    # Retrieve chat history from the database for the specific user
    with app.app_context():
        chat_history_db = Chat.query.filter_by(user_id=user_id).order_by(Chat.timestamp).all()
        history = []
        for chat in chat_history_db:
            history.append({"role": "user", "parts":[chat.user_message]})
            history.append({"role": "model", "parts": [chat.bot_response]})
        
        dynamic_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
        
        )
        print(f"User {user_id} IQ: {iq_score} | Using system instruction: {system_instruction}")
        chat_session = dynamic_model.start_chat(history=history)
        response = chat_session.send_message(user_message)
        model_response = response.text

        # Store the new interaction in the database
        new_chat = Chat(user_id=user_id, user_message=user_message, bot_response=model_response)
        db.session.add(new_chat)
        db.session.commit()

        return jsonify({'response': model_response})
    
@app.route('/history/<user_id>', methods=['GET'])
def get_chat_history(user_id):
    print("hi")
    with app.app_context():
        try:
            chat_history_db = Chat.query.filter_by(user_id=user_id).order_by(Chat.timestamp).all()
            history = []
            for chat in chat_history_db:
                history.append({"role": "user", "text": chat.user_message})
                history.append({"role": "model", "text": chat.bot_response})
        except:
            initial_bot_response = "Hello! I'm your Python instructor. What's your IQ level so I can tailor our learning?"
            new_chat = Chat(user_id=user_id, user_message="", bot_response=initial_bot_response)
            db.session.add(new_chat)
            db.session.commit()
            history.append({"role": "model", "parts": [initial_bot_response]})
        return jsonify(history)

if __name__ == '__main__':
    app.run(debug=True)