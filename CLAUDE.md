# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Grade 1 Math Quiz web app aligned to Ontario curriculum. Students select a math strand, answer questions, and get AI-powered tutoring when they're stuck.

## Commands

```bash
# Install dependencies
uv sync

# Run dev server (port 5001 to avoid macOS conflict on 5000)
PORT=5001 uv run python app.py

# Production
gunicorn app:app
```

Required env vars (in `.env`):
- `GEMINI_API_KEY` — for mascot + chatbot
- `SECRET_KEY` — Flask session secret
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — OAuth (optional for dev)
- `DATABASE_URL` — PostgreSQL (falls back to `history.json` if unset)

## Architecture

**`app.py`** — Flask app. Key routes:
- `GET /quiz/<strand>` — serves quiz UI
- `GET /api/get_question/<strand>` — generates a random question
- `POST /api/mascot` — calls Gemini to produce short contextual encouragement (states: `start`, `correct`, `wrong`, `streak3`, `streak5`, `finish`)
- `POST /api/chat` — Gemini tutoring chatbot for wrong answers, returns JSON with `reply` + optional `animation` (blocks/apples for visual math)
- `POST /api/save_session` — persists quiz session to DB or localStorage (guests)

**`curriculum.py`** — All question generators. Each strand (`number`, `algebra`, `spatial`, `data`, `financial`, `coding`, `placevalue`, `time`, `measurement`, `wordproblems`, `comparing`, `skipcounting`) has its own class. Uses lazy `set_translator()` for i18n to avoid startup slowness.

**`chatbot.py`** — Gemini chatbot logic. Returns structured JSON with `reply` and `animation` fields. Grade-1-appropriate tone enforced via system instruction.

**`templates/quiz.html`** — All quiz interactivity in one file. The mascot is a cat (`😸`) in the bottom-right corner. `updateMascot(state, question, userAnswer, correctAnswer)` calls `/api/mascot` and speaks the response via Web Speech API (`speakAndAnimate`). CSS classes `mascot-jump` / `mascot-shake` drive animations.

## Localization

Flask-Babel supports English/French. All user-facing strings in templates use `{{ _('...') }}`, in Python use `_()`. Locale selection: session `lang` key → `Accept-Language` header. The `set_translator(_)` call in `app.py` passes the translator to `curriculum.py` at startup.

## Database

PostgreSQL with connection pool (min 1, max 10). Tables: `users`, `history` (JSONB). Falls back to `history.json` for local dev. `init_db()` runs on startup and is idempotent.

## Deployment

Configured for Railway/Heroku via `ProxyFix` (ensures `url_for` generates `https://` URLs behind a reverse proxy). Port comes from `PORT` env var, defaults to 5000.

---

# gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

To install gstack: `git clone https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`

Available gstack skills:
- `/office-hours` — structured Q&A / design discussion
- `/plan-ceo-review` — prepare a plan for CEO review
- `/plan-eng-review` — prepare a plan for engineering review
- `/plan-design-review` — prepare a plan for design review
- `/design-consultation` — get design feedback
- `/review` — code / PR review
- `/ship` — ship a feature end-to-end
- `/browse` — headless browser for web browsing and QA
- `/qa` — full QA pass on a feature
- `/qa-only` — QA without setup steps
- `/design-review` — review visual design
- `/setup-browser-cookies` — configure browser cookies for authenticated browsing
- `/retro` — run a retrospective
- `/debug` — systematic debugging workflow
- `/document-release` — document a release
