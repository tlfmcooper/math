import json
import os
import uuid 
from flask import Flask, render_template, request, jsonify
from curriculum import generate_question

app = Flask(__name__)
HISTORY_FILE = 'history.json'

# Valid strands for input validation
VALID_STRANDS = {
    'number', 'algebra', 'spatial', 'data', 'financial', 'coding',
    'placevalue', 'time', 'measurement', 'wordproblems', 'comparing', 'skipcounting'
}

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_history(record):
    history = load_history()
    history.append(record)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz/<strand>')
def quiz(strand):
    if strand not in VALID_STRANDS:
        return "Invalid strand", 400
    return render_template('quiz.html', strand=strand)

@app.route('/api/get_question/<strand>')
def api_question(strand):
    if strand not in VALID_STRANDS:
        return jsonify({"error": "Invalid strand"}), 400
    return jsonify(generate_question(strand))

@app.route('/api/save_session', methods=['POST'])
def save_session():
    data = request.json
    # Assign a unique ID for the review link
    data['id'] = str(uuid.uuid4())
    save_history(data)
    return jsonify({"status": "success"})

@app.route('/history')
def history():
    data = load_history()
    # Reverse to show newest first
    return render_template('history.html', history=data[::-1])

@app.route('/review/<session_id>')
def review_session(session_id):
    history = load_history()
    # Find the specific session by ID
    session = next((item for item in history if item.get('id') == session_id), None)
    
    if not session:
        return "Session not found", 404
        
    return render_template('review.html', session=session)

if __name__ == '__main__':
    app.run(debug=True, port=5000)