# PocketSmart AI

Complete FastAPI + Jinja2 implementation of the supplied PocketSmart AI project documentation.

Features:
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image
- Gemini multimodal recommendation layer
- User registration/login/logout
- JWT authentication and browser session
- Recommendation history and details
- Budget allocation and recommendation cards
- Platform search links for Amazon, Flipkart, IKEA, Swiggy, Zomato and OYO
- Responsive HTML/CSS/JavaScript frontend
- SQLite database by default
- Automated tests

## Technology decision
The supplied document mentions Flask in early architecture text and later defines FastAPI/Jinja2 milestones, routes and startup behavior. This implementation follows the later, explicit architecture: FastAPI + Jinja2.

The document also asks for mock/simulated sourcing from third-party platforms. No private retailer/vendor APIs or credentials are provided, so this implementation does not fabricate live catalog data. Gemini produces recommendation candidates and the backend creates real platform search URLs for the candidate.

## Prerequisites
- Python 3.11+
- VS Code
- Gemini API key for live AI recommendations
- No separate Amazon/Flipkart/IKEA/Swiggy/Zomato/OYO credentials are required by this implementation
- SQLite is automatic

## Setup
Windows:
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set in `.env`:
```env
GEMINI_API_KEY=your_real_key
SECRET_KEY=your_long_random_secret
```

Run:
```bash
uvicorn app.main:app --reload
```
or:
```bash
python run.py
```

Open http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

## Gemini model
The documentation calls the model "Gemini 1.5 Flash Pro". The API model identifier is configurable because model availability/naming can vary. The default is:
```env
GEMINI_MODEL=gemini-1.5-flash
```
Change only that variable if the Gemini account exposes another compatible model.

## Environment
- `APP_NAME`
- `ENVIRONMENT`
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_TEMPERATURE`
- `CORS_ORIGINS`
- `SESSION_MAX_AGE`
- `MAX_UPLOAD_MB`

## Main routes
Pages:
`/`, `/testimonials`, `/register`, `/login`, `/dashboard`, `/home-planner`, `/party-planner`, `/jewelry-planner`, `/history-page`, `/recommendations`

API:
`POST /register`, `POST /login`, `POST /token`, `GET /logout`, `GET /session-info`, `GET /session-data`, `POST /generate-home`, `POST /generate-party`, `POST /generate-jewelry`, `GET /recommendations-details/{id}`, `GET /history`, `GET /startup`, `GET /health`

## Database
SQLite is created automatically at `data/pocketsmart.db`.

## Testing
```bash
pytest -q
```

Tests use a temporary SQLite database and no live Gemini request.

## Production notes
For public deployment, use HTTPS, secure cookies, PostgreSQL, a secrets manager, rate limiting, restricted CORS, and a production process manager/reverse proxy.
