import json
import os
import uuid
from flask import Flask, render_template, request, jsonify
from curriculum import generate_question
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
HISTORY_FILE = 'history.json'
DATABASE_URL = os.environ.get('DATABASE_URL')

# Valid strands for input validation
VALID_STRANDS = {
    'number', 'algebra', 'spatial', 'data', 'financial', 'coding',
    'placevalue', 'time', 'measurement', 'wordproblems', 'comparing', 'skipcounting'
}

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    if DATABASE_URL:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                data JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()

def load_history():
    if not DATABASE_URL:
        if not os.path.exists(HISTORY_FILE):
            return []
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT data FROM history ORDER BY created_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row['data'] for row in rows]

def save_history(record):
    if not DATABASE_URL:
        history = load_history()
        history.append(record)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO history (id, data) VALUES (%s, %s)',
                (record['id'], json.dumps(record)))
    conn.commit()
    cur.close()
    conn.close()

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
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    init_db()