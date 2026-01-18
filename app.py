import json
import os
import uuid
from dotenv import load_dotenv
load_dotenv()  # Load .env file before accessing env vars

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from curriculum import generate_question
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
HISTORY_FILE = 'history.json'
DATABASE_URL = os.environ.get('DATABASE_URL')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

class User(UserMixin):
    def __init__(self, id, google_id, email, name, picture):
        self.id = id
        self.google_id = google_id
        self.email = email
        self.name = name
        self.picture = picture

@login_manager.user_loader
def load_user(user_id):
    if not DATABASE_URL:
        return None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, google_id, email, name, picture FROM users WHERE id = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return User(row['id'], row['google_id'], row['email'], row['name'], row['picture'])
    return None

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
        # Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                name TEXT,
                picture TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # History table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                data JSONB NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add user_id column if it doesn't exist (for existing tables)
        cur.execute('''
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                               WHERE table_name='history' AND column_name='user_id') THEN
                    ALTER TABLE history ADD COLUMN user_id INTEGER REFERENCES users(id);
                END IF;
            END $$;
        ''')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id)')
        conn.commit()
        cur.close()
        conn.close()

def load_history(user_id=None):
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
    if user_id:
        cur.execute('SELECT data FROM history WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
    else:
        cur.execute('SELECT data FROM history WHERE user_id IS NULL ORDER BY created_at DESC')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row['data'] for row in rows]

def save_history(record, user_id=None):
    if not DATABASE_URL:
        history = load_history()
        history.append(record)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        return
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO history (id, data, user_id) VALUES (%s, %s, %s)',
                (record['id'], json.dumps(record), user_id))
    conn.commit()
    cur.close()
    conn.close()

def get_or_create_user(google_id, email, name, picture):
    if not DATABASE_URL:
        # For local dev without DB, create a simple user object
        # Use google_id hash as a simple numeric ID
        user_id = abs(hash(google_id)) % 1000000
        return User(user_id, google_id, email, name, picture)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, google_id, email, name, picture FROM users WHERE google_id = %s', (google_id,))
    row = cur.fetchone()
    if row:
        user = User(row['id'], row['google_id'], row['email'], row['name'], row['picture'])
    else:
        cur.execute(
            'INSERT INTO users (google_id, email, name, picture) VALUES (%s, %s, %s, %s) RETURNING id',
            (google_id, email, name, picture)
        )
        user_id = cur.fetchone()['id']
        conn.commit()
        user = User(user_id, google_id, email, name, picture)
    cur.close()
    conn.close()
    return user

@app.route('/')
def index():
    return render_template('index.html', user=current_user)

@app.route('/login')
def login():
    if not os.environ.get('GOOGLE_CLIENT_ID'):
        return "Google OAuth not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.", 500
    redirect_uri = url_for('auth_callback', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = google.authorize_access_token()
    userinfo = token.get('userinfo')
    if userinfo:
        user = get_or_create_user(
            google_id=userinfo['sub'],
            email=userinfo['email'],
            name=userinfo.get('name'),
            picture=userinfo.get('picture')
        )
        login_user(user)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

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
def save_session_route():
    data = request.json
    # Assign a unique ID for the review link
    data['id'] = str(uuid.uuid4())
    user_id = current_user.id if current_user.is_authenticated else None
    save_history(data, user_id)
    return jsonify({"status": "success"})

@app.route('/history')
def history():
    user_id = current_user.id if current_user.is_authenticated else None
    data = load_history(user_id)
    return render_template('history.html', history=data, user=current_user)

@app.route('/review/<session_id>')
def review_session(session_id):
    user_id = current_user.id if current_user.is_authenticated else None
    history_data = load_history(user_id)
    # Find the specific session by ID
    session_data = next((item for item in history_data if item.get('id') == session_id), None)

    if not session_data:
        return "Session not found", 404

    return render_template('review.html', session=session_data, user=current_user)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    init_db()