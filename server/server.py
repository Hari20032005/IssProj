import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import hmac
import os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

app = Flask(__name__)
CORS(app)

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# In-memory storage (replace with a database in a real application)
users = {}
messages = []

# Generate a random secret key (in a real app, use a secure key management system)
SECRET_KEY = os.urandom(32)

# Load the pre-trained model and vectorizer
with open('spam_model.pkl', 'rb') as f:
    spam_model = pickle.load(f)
with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stopwords and non-alphabetic tokens
    stop_words = set(stopwords.words('english'))
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    return ' '.join(tokens)

def is_spam(message):
    # Preprocess the message
    preprocessed_message = preprocess_text(message)
    # Transform the message using the pre-trained vectorizer
    message_vector = vectorizer.transform([preprocessed_message])
    # Predict using the pre-trained model
    prediction = spam_model.predict(message_vector)[0]
    return bool(prediction)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    
    users[username] = password
    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username not in users or users[username] != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    return jsonify({"message": "Login successful"}), 200

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get('sender')
    recipient = data.get('recipient')
    content = data.get('content')
    
    spam_detected = is_spam(content)
    
    # Create HMAC-SHA256
    hmac_sha256 = hmac.new(SECRET_KEY, content.encode(), hashlib.sha256).hexdigest()
    
    message = {
        "sender": sender,
        "recipient": recipient,
        "content": content,
        "hmac": hmac_sha256,
        "spam_detected": spam_detected
    }
    messages.append(message)
    return jsonify({"message": "Message sent successfully", "spam_detected": spam_detected}), 201

@app.route('/get_messages', methods=['GET'])
def get_messages():
    return jsonify(messages)

if __name__ == '__main__':
    app.run(debug=True)