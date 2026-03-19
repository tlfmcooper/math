import json
import os
import uuid
from dotenv import load_dotenv
load_dotenv()  # Load .env file before accessing env vars

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, g
from curriculum import generate_question, set_translator
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_babel import Babel, gettext as _
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
# Fix for running behind a reverse proxy (Railway, Heroku, etc.)
# This ensures url_for generates https:// URLs in production
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
HISTORY_FILE = 'history.json'
DATABASE_URL = os.environ.get('DATABASE_URL')

# Database connection pool (lazy initialization)
_db_pool = None
_db_initialized = False

def get_db_pool():
    """Get or create the database connection pool."""
    global _db_pool
    if _db_pool is None and DATABASE_URL:
        _db_pool = pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
    return _db_pool

# Flask-Babel configuration for i18n
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr']

def get_locale():
    # Check user preference in session first
    if 'lang' in session:
        return session['lang']
    # Then check browser Accept-Language header
    return request.accept_languages.best_match(['en', 'fr'], default='en')

babel = Babel(app, locale_selector=get_locale)

# Rate limiter — protects AI endpoints from abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

# Set the translator for curriculum.py to use
set_translator(_)

@app.before_request
def before_request():
    g.locale = get_locale()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth setup - use static endpoints to avoid slow metadata fetch on startup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    access_token_url='https://oauth2.googleapis.com/token',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
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
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT id, google_id, email, name, picture FROM users WHERE id = %s', (user_id,))
        row = cur.fetchone()
        cur.close()
        if row:
            return User(row['id'], row['google_id'], row['email'], row['name'], row['picture'])
        return None
    finally:
        release_db_connection(conn)

# Valid strands for input validation
VALID_STRANDS = {
    'number', 'algebra', 'spatial', 'data', 'financial', 'coding',
    'placevalue', 'time', 'measurement', 'wordproblems', 'comparing', 'skipcounting'
}

def get_db_connection():
    """Get a connection from the pool."""
    db_pool = get_db_pool()
    if db_pool:
        conn = db_pool.getconn()
        # Set cursor factory for this connection
        return conn
    return None

def release_db_connection(conn):
    """Return a connection to the pool."""
    db_pool = get_db_pool()
    if db_pool and conn:
        db_pool.putconn(conn)

def init_db():
    """Initialize database tables. Only runs once per process."""
    global _db_initialized
    if _db_initialized or not DATABASE_URL:
        return

    conn = get_db_connection()
    if not conn:
        return

    try:
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
        _db_initialized = True
    finally:
        release_db_connection(conn)

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
    if not conn:
        return []
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if user_id:
            cur.execute('SELECT data FROM history WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
        else:
            cur.execute('SELECT data FROM history WHERE user_id IS NULL ORDER BY created_at DESC')
        rows = cur.fetchall()
        cur.close()
        return [row['data'] for row in rows]
    finally:
        release_db_connection(conn)

def save_history(record, user_id=None):
    if not DATABASE_URL:
        history = load_history()
        history.append(record)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
        return
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO history (id, data, user_id) VALUES (%s, %s, %s)',
                    (record['id'], json.dumps(record), user_id))
        conn.commit()
        cur.close()
    finally:
        release_db_connection(conn)

def get_or_create_user(google_id, email, name, picture):
    if not DATABASE_URL:
        # For local dev without DB, create a simple user object
        # Use google_id hash as a simple numeric ID
        user_id = abs(hash(google_id)) % 1000000
        return User(user_id, google_id, email, name, picture)

    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
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
        return user
    finally:
        release_db_connection(conn)

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

@app.route('/lang/<lang>')
def set_language(lang):
    if lang in ['en', 'fr']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/quiz/<strand>')
def quiz(strand):
    if strand not in VALID_STRANDS:
        return "Invalid strand", 400
    return render_template('quiz.html', strand=strand, user=current_user)

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

def _sanitize_prompt_field(value, max_len=200):
    """Strip newlines and truncate user-supplied values before embedding in prompts."""
    return str(value).replace('\n', ' ').replace('\r', ' ').replace('"', "'")[:max_len]


@app.route('/api/mascot', methods=['POST'])
@limiter.limit('10 per minute')
def api_mascot():
    import logging
    from google.genai import types
    from chatbot import _get_client
    data = request.json
    state = data.get('state', 'correct')
    # Sanitize user-supplied fields before embedding in prompts
    question = _sanitize_prompt_field(data.get('question', ''))
    user_answer = _sanitize_prompt_field(data.get('user_answer', ''))
    correct_answer = _sanitize_prompt_field(data.get('correct_answer', ''))

    client = _get_client()
    if not client:
        return jsonify({"message": "You are doing great!"})

    prompts = {
        'correct': f"A Grade 1 student just answered the math question '{question}' correctly with '{user_answer}'. Give ONE short excited reaction that mentions what they just did right (max 12 words, no quotes, keep it fun and specific).",
        'wrong': f"A Grade 1 student answered '{user_answer}' to the math question '{question}'. Give ONE warm, specific encouragement that acknowledges their try without revealing '{correct_answer}' (max 12 words, no quotes).",
        'streak3': "A Grade 1 student just got 3 math questions correct in a row! ONE very excited reaction, max 10 words, no quotes.",
        'streak5': "A Grade 1 student just got 5 math questions correct in a row — on a roll! ONE super excited reaction, max 10 words, no quotes.",
        'finish': "A Grade 1 student just finished a math quiz. ONE warm proud send-off, max 10 words, no quotes.",
        'start': "You are a friendly cat mascot welcoming a Grade 1 student to their math quiz. ONE warm, playful greeting, max 8 words, no quotes.",
    }
    prompt = prompts.get(state, prompts['start'])

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.95, max_output_tokens=50)
        )
        message = response.text.strip().strip('"').strip("'")
        return jsonify({"message": message})
    except Exception as e:
        logging.error(f"Mascot error: {e}")
        return jsonify({"message": "Keep going, you are amazing!"})

@app.route('/api/chat', methods=['POST'])
@limiter.limit('10 per minute')
def api_chat():
    data = request.json
    # Sanitize user-supplied fields before embedding in prompts
    question = _sanitize_prompt_field(data.get('question', ''))
    user_answer = _sanitize_prompt_field(data.get('user_answer', ''))
    correct_answer = _sanitize_prompt_field(data.get('correct_answer', ''))
    messages = data.get('messages', [])
    strand = data.get('strand', 'number')
    attempt = max(1, int(data.get('attempt', 1)))

    # Validate strand to prevent prompt injection via this field
    if strand not in VALID_STRANDS:
        strand = 'number'

    context = f"Question: {question} | Student answered: {user_answer} | Correct answer was: {correct_answer}."

    try:
        from chatbot import get_chat_response
        response_data = get_chat_response(messages, context, strand=strand, attempt=attempt)
        if "error" in response_data:
            return jsonify(response_data), 500
        return jsonify(response_data)
    except ImportError:
        return jsonify({"error": "Chatbot module not found or missing dependencies."}), 500

@app.route('/history')
def history():
    user_id = current_user.id if current_user.is_authenticated else None
    data = load_history(user_id)
    return render_template('history.html', history=data, user=current_user)

@app.route('/review/<session_id>')
def review_session(session_id):
    # Handle local reviews (stored in browser localStorage)
    if session_id == 'local':
        return render_template('review.html', session=None, user=current_user, is_local=True)

    user_id = current_user.id if current_user.is_authenticated else None
    history_data = load_history(user_id)
    # Find the specific session by ID
    session_data = next((item for item in history_data if item.get('id') == session_id), None)

    if not session_data:
        return "Session not found", 404

    return render_template('review.html', session=session_data, user=current_user, is_local=False)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
else:
    init_db()