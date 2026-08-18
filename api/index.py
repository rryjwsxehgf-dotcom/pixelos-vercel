from flask import Flask, request, jsonify, send_from_directory
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core import generate_chat_reply

app = Flask(__name__, static_folder='../public', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('../public', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    chat_id = data.get("chat_id", 1)
    message = data.get("message", "")
    
    if not message:
        return jsonify({"error": "Empty message"}), 400
        
    reply = generate_chat_reply(chat_id, message)
    return jsonify({"reply": reply})

app = app
