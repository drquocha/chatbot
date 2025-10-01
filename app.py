from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from chatbot import SimpleChatbot

load_dotenv()

app = Flask(__name__)
chatbot = SimpleChatbot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': 'Tin nhắn không được để trống'}), 400

    response = chatbot.get_response(user_message)
    return jsonify({'response': response})

@app.route('/clear', methods=['POST'])
def clear_history():
    chatbot.clear_history()
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)