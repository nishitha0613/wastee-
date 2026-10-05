# Smart Waste Management Backend API

Production-ready FastAPI backend service for the **Smart AI Assistant for Waste Disposal Guidance** (**EcoCycle**).

---

## Tech Stack

- **Python** (>= 3.10)
- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: ASGI web server
- **SQLite / PostgreSQL**: Multi-database compatibility via SQLAlchemy ORM
- **Alembic**: Database schema migrations
- **Pydantic v2 / Pydantic Settings**: Request validation and typed settings
- **bcrypt**: Password hashing using salted bcrypt (cost factor 12)
- **PyJWT**: Stateless HMAC-SHA256 (HS256) JSON Web Tokens
- **Pillow**: Safe image validation, decoding, resize, and corruption checks
- **pytest**: Automated testing suite with isolated test database

---

## Architecture & Directory Structure

```
backend/
├── alembic/                      # Database schema migrations
│   ├── env.py                    # Alembic runtime environment
│   └── versions/                 # Migration scripts
├── alembic.ini                   # Alembic configuration
├── app/
│   ├── config.py                 # Pydantic Settings from .env
│   ├── database.py               # Engine configuration (SQLite/Postgres), session & events
│   ├── init_db.py                # Standalone table creation CLI script
│   ├── seed_admin.py             # Administrator account seed CLI script
│   ├── main.py                   # FastAPI application, lifespan, CORS, and error handling
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py               # User model & roles (user, admin)
│   │   ├── waste_report.py       # WasteReport model & foreign keys
│   │   └── collection_request.py # CollectionRequest model & lifecycle states
│   ├── routers/                  # API endpoints
│   │   ├── health.py             # Health check (/api/health)
│   │   ├── auth.py               # Authentication & token endpoints (/api/auth/*)
│   │   ├── waste.py              # Waste classification & paginated reports (/api/waste/*)
│   │   ├── collection.py         # Citizen collection requests (/api/collection-requests/*)
│   │   └── admin_collection.py   # Admin search, filter, and state transitions (/api/admin/*)
│   ├── schemas/                  # Pydantic validation schemas
│   │   ├── pagination.py         # Standardized PaginatedResponse[T]
│   │   ├── user.py
│   │   ├── waste_report.py
│   │   └── collection_request.py
│   ├── services/                 # Pluggable business logic
│   │   ├── storage.py            # Abstract BaseStorageService & LocalStorageService
│   │   ├── waste_classifier.py   # Modular AI/ML classifier (ONNX & heuristic fallbacks)
│   │   └── disposal_guidance.py  # Structured municipal disposal guidance
│   └── utils/
│       ├── security.py           # bcrypt hashing & JWT utilities
│       └── dependencies.py       # Auth guards (get_current_user, get_current_admin)
├── tests/                        # Automated Pytest suite
│   ├── conftest.py               # Isolated test database and TestClient fixtures
│   ├── test_auth.py              # Authentication tests
│   ├── test_authorization.py     # Authorization & permission tests
│   ├── test_waste.py             # Image upload, validation & AI classification tests
│   ├── test_collection.py        # Collection requests lifecycle tests
│   ├── test_admin_workflow.py    # Admin state machine & statistics tests
│   ├── test_database.py          # Database integrity, foreign keys, & rollback tests
│   └── test_search_filter_pagination.py # Search, filtering, and pagination tests
├── uploads/                      # Local uploaded image directory (.gitkeep)
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Production & testing dependencies
├── .env.example                  # Environment configuration template
└── README.md
```

---

## Environment Variables

Configure application settings in `.env` (copy from `.env.example`):

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./waste_management.db` | SQLAlchemy database connection string (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | *Secret* | 32+ char cryptographic secret used to sign JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `1440` (24h) | JWT access token validity period in minutes |
| `FRONTEND_URL` | `http://localhost:3000` | Frontend web URL automatically whitelisted in CORS |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Comma-separated list of allowed CORS origins |
| `MAX_UPLOAD_SIZE` | `5242880` (5MB) | Maximum allowed file upload size in bytes |
| `AI_CONFIDENCE_THRESHOLD` | `0.60` | Minimum score threshold for classifying into distinct categories |
| `ADMIN_NAME` | `System Administrator` | Default admin name for seed script |
| `ADMIN_EMAIL` | `admin@ecocycle.com` | Default admin email for seed script |
| `ADMIN_PASSWORD` | *ChangeThisPassword123!* | Default admin password for seed script |

---

## Database Setup & Migrations

### 1. SQLite (Local Development)
By default, the backend operates with an embedded SQLite database (`waste_management.db`) with foreign key pragma enforcement.

### 2. PostgreSQL (Production Deployment)
Set `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ecocycle_db
```
The application dynamically adjusts connection pool parameters (`pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`) without requiring code changes.

### 3. Alembic Migration Commands
Run database migrations using Alembic:

```bash
# Check current migration status
alembic current

# Apply all pending migrations to the latest version
alembic upgrade head

# Generate a new migration after updating SQLAlchemy models
alembic revision --autogenerate -m "describe_changes"

# Rollback one migration step
alembic downgrade -1
```

---

## Local Setup & Run Commands

### 1. Initialize Virtual Environment & Install Dependencies
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Migrations & Seed Default Administrator
```bash
alembic upgrade head
python -m app.seed_admin
```

### 3. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000 --host 127.0.0.1
```
- **API URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **Alternative ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## Running Automated Tests

The testing suite runs against an **isolated SQLite test database** and does not touch development data.

```bash
# Run entire test suite (61 tests)
pytest

# Run tests with verbose output
pytest -v

# Run search, filter, and pagination tests only
pytest tests/test_search_filter_pagination.py -v
```

From the repository root:
```bash
npm test
```

---

## Search, Filtering & Pagination API Reference

### 1. Paginated User Waste Reports
`GET /api/waste/reports?page=1&limit=10`

**Response (`200 OK`):**
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 2,
      "waste_type": "Plastic",
      "confidence": 0.94,
      "image_path": "/uploads/123.jpg",
      "description": null,
      "guidance": {
        "category": "Plastic",
        "disposal_method": "Rinse, dry, and place into the dry recyclable stream.",
        "do": ["Rinse containers"],
        "dont": ["Do not burn"],
        "recyclable": true,
        "collection_recommended": false
      },
      "created_at": "2026-10-05T20:00:00Z"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 1,
  "total_pages": 1
}
```

### 2. Paginated User Collection Requests
`GET /api/collection-requests?page=1&limit=10`

### 3. Admin Search, Filtering & Pagination
`GET /api/admin/collection-requests?status=submitted&waste_type=Plastic&search=Green&from_date=2026-10-01&to_date=2026-10-31&page=1&limit=10`

**Parameters:**
- `status` (*optional*): Filter by status (`submitted`, `accepted`, `scheduled`, `collected`, `completed`, `rejected`)
- `waste_type` (*optional*): Filter by category (`Plastic`, `Organic`, `E-Waste`, etc.)
- `from_date` / `to_date` (*optional*): ISO-8601 or YYYY-MM-DD date range
- `search` (*optional*): Substring search across citizen name, citizen email, waste type, and location
- `page` (*optional*, default: `1`, min: `1`): Current page
- `limit` (*optional*, default: `10`, min: `1`, max: `100`): Results per page
