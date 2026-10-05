# Smart AI Assistant for Waste Disposal Guidance (EcoCycle)

A modern full-stack web application designed to help citizens and municipal authorities identify, segregate, report, and manage solid waste responsibly using AI-powered image recognition and automated collection workflows.

---

## 1. Project Overview

**EcoCycle** bridges the communication gap between citizens and municipal waste management teams:
- **Citizens** upload photos of discarded items or community waste piles. The system instantly detects the waste category, assesses AI confidence, provides structured disposal guidance (Do's and Don'ts, recycling potential), and allows one-click scheduling of waste collection requests.
- **Municipal Administrators** access a centralized dispatch command center to monitor all incoming requests, search and filter by status, waste category, location, and date range, advance requests through a strict state machine lifecycle, and review operational analytics.

---

## 2. Features

- **AI Waste Classification**: Multi-category recognition across Organic, Plastic, Paper, Glass, Metal, E-Waste, Hazardous, and Other.
- **Dynamic Disposal Guidance**: Actionable Do's and Don'ts, recyclability status, and tailored disposal methods.
- **Confidence Scoring & Low-Confidence Safeguards**: Transparent confidence percentages; items below threshold (60%) default safely to 'Other' with manual review recommendations.
- **Citizen Collection Requests**: Link photo scans directly to collection requests with volume, landmark location, and special instructions.
- **Real-Time Request Lifecycle Tracking**: Visual progression tracker through `Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Scheduled` $\rightarrow$ `Collected` $\rightarrow$ `Completed` (or `Rejected`).
- **Role-Based Authentication**: Secure JWT-based authentication separating regular citizens from authorized municipal administrators.
- **Municipal Admin Command Center**: Comprehensive table with real-time status counters, multi-field search (by citizen name, email, location, waste type), status filtering, and date range filtering.
- **Secure File Upload Handling**: MIME type verification, magic-byte inspection (JPEG, PNG, WEBP), 5MB size limits, and path traversal protection.
- **Database Schema & Migrations**: Multi-engine SQLAlchemy ORM supporting local SQLite and production PostgreSQL with Alembic migrations.
- **Paginated Endpoints**: Standardized pagination across waste reports and collection request registries.

---

## 3. Architecture

The application is structured into decoupled frontend, backend, and persistence layers:

```
├── src/                          # React Frontend (Vite)
│   ├── components/               # UI components (Hero, Scanner, Reports, Admin, Auth)
│   ├── context/                  # AuthContext (JWT management & session broadcast)
│   ├── services/                 # Centralized api.js client (token injection, error normalization)
│   └── index.css                 # Custom CSS design system (Responsive, Accessible)
├── backend/                      # FastAPI Python Backend
│   ├── app/
│   │   ├── routers/              # API Endpoints (auth, waste, collection, admin_collection, health)
│   │   ├── models/               # SQLAlchemy ORM models (User, WasteReport, CollectionRequest)
│   │   ├── schemas/              # Pydantic v2 validation models & paginated schemas
│   │   ├── services/             # AI classifier, disposal guidance, and storage services
│   │   ├── utils/                # Security (bcrypt, JWT) and FastAPI dependencies
│   │   ├── database.py           # Engine & connection pool configuration
│   │   └── config.py             # Typed Pydantic Settings
│   ├── alembic/                  # Database migration versions
│   ├── tests/                    # 61 Automated Pytest tests (isolated test database)
│   └── Dockerfile                # Production multi-stage container
├── docker-compose.yml            # Production PostgreSQL + FastAPI container orchestration
└── render.yaml                   # Cloud deployment blueprint (Render)
```

---

## 4. Frontend Setup

### Prerequisites
- **Node.js** (v18+ recommended)
- **npm** (v9+)

### Installation
```bash
# From the project root:
npm install
```

### Environment Configuration
The frontend automatically references `VITE_API_URL`. Create or verify `.env`:
```properties
VITE_API_URL=http://localhost:8000
```

---

## 5. Backend Setup

### Prerequisites
- **Python** (v3.10+; tested on Python 3.12 and 3.14)
- **pip** and `venv`

### Installation
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 6. Environment Variables

Create `backend/.env` (or copy from `backend/.env.example`):

| Variable | Default Value | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./waste_management.db` | SQLAlchemy connection string (SQLite or PostgreSQL) |
| `JWT_SECRET_KEY` | *Secret* | 32+ char cryptographic secret for signing JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| `1440` (24h) | JWT validity window |
| `FRONTEND_URL` | `http://localhost:3000` | Deployed frontend domain allowed in CORS |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Whitelisted CORS origin list |
| `MAX_UPLOAD_SIZE` | `5242880` (5MB) | Maximum file size in bytes |
| `AI_CONFIDENCE_THRESHOLD` | `0.60` | Minimum score required for distinct category classification |
| `ADMIN_NAME` | `System Administrator` | Default admin seed name |
| `ADMIN_EMAIL` | `admin@ecocycle.com` | Default admin seed email |
| `ADMIN_PASSWORD` | `Admin@Secure123!` | Default admin seed password |

---

## 7. Database Setup & Migrations

### Local Development (SQLite)
By default, SQLite is used at `backend/waste_management.db` with SQLite foreign key pragma enforcement.

### Production (PostgreSQL)
Supply a PostgreSQL URI:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ecocycle_db
```
SQLAlchemy automatically applies connection pooling (`pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`).

### Running Alembic Migrations
```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.seed_admin
```

---

## 8. AI Model Setup

The waste classification architecture is isolated behind `app/services/waste_classifier.py`:
1. **Production Deep Learning**: If an ONNX model weight file is placed at `backend/app/models_ml/waste_classifier.onnx`, `ONNXWasteClassifier` automatically loads the model session once into memory for fast inference.
2. **Development & Fallback Classifier**: When no trained weight file is present, `DevelopmentWasteClassifier` runs image validation, preprocessing, Pillow dimension/mode conversion, variance and visual feature extraction, and confidence thresholding.
3. **Thresholding**: Classifications with confidence $< 0.60$ automatically map to `Other` with an advisory notice to inspect labeling.

---

## 9. Local Development

Start both services concurrently:

### Terminal 1 — Backend API
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 127.0.0.1
```

### Terminal 2 — Frontend Application
```bash
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 10. Running Tests

### Backend Automated Test Suite (61 Tests)
The test suite utilizes an isolated, temporary SQLite database fixture and does not alter development records:
```bash
# From backend directory:
cd backend
source .venv/bin/activate
pytest -v

# Or from project root:
npm test
```

### End-to-End Live Audit Script
Run the automated verification suite against the running local server:
```bash
backend/.venv/bin/python3 audit_suite.py
```

---

## 11. API Documentation

Interactive API documentation is generated by FastAPI:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`
- **Health Check**: `GET http://localhost:8000/api/health`

---

## 12. User Workflow

1. **Register / Login**: Citizen creates an account or logs in with email and password (`POST /api/auth/register`, `POST /api/auth/login`).
2. **Scan Waste**: Citizen selects or uploads an image (JPG, PNG, WEBP).
3. **AI Identification**: Image is analyzed by `POST /api/waste/identify`, returning waste type, confidence score, and disposal guidance.
4. **Request Collection**: Citizen clicks "Request Collection", fills in quantity and pickup location, and submits (`POST /api/collection-requests`).
5. **Track Status**: Under "My Reports", citizen tracks status changes in real-time (`Submitted` $\rightarrow$ `Accepted` $\rightarrow$ `Scheduled` $\rightarrow$ `Collected` $\rightarrow$ `Completed`).

---

## 13. Admin Workflow

1. **Admin Authentication**: Admin logs in using administrative credentials (`admin@ecocycle.com`).
2. **Command Center**: Admin accesses "All Reports" with overview metrics (Submitted, In Progress, Completed, Rejected).
3. **Search & Filter**: Admin searches by citizen name, email, location, or filters by status and date range.
4. **Workflow Execution**:
   - **Accept**: `PATCH /api/admin/collection-requests/{id}/accept`
   - **Schedule**: `PATCH /api/admin/collection-requests/{id}/schedule` with date/time
   - **Collect**: `PATCH /api/admin/collection-requests/{id}/collect`
   - **Complete**: `PATCH /api/admin/collection-requests/{id}/complete`
   - **Reject**: `PATCH /api/admin/collection-requests/{id}/reject` (optional reason)
5. **Analytics**: Admin monitors collection statistics (`GET /api/admin/collection-requests/stats`).

---

## 14. Deployment Instructions

### Option A: Docker Compose (Local or Virtual Machine)
```bash
docker-compose up --build -d
```
Starts PostgreSQL on port 5432 and FastAPI on port 8000.

### Option B: Cloud Hosting (Render / Railway / Fly.io)
A ready-to-deploy [render.yaml](render.yaml) blueprint is included:
1. Connect your Git repository to Render.
2. Render creates the PostgreSQL database, runs migrations and seeding via `backend/start.sh`, and starts the web service.
3. Deploy the frontend as a Static Site pointing `VITE_API_URL` to your backend URL.

---

## 15. Known Limitations

1. **Pre-trained Deep Learning Model Artifact**: The development classifier uses Pillow image validation and color/feature heuristics. To activate neural network inference, place a trained `.onnx` model at `backend/app/models_ml/waste_classifier.onnx`.
2. **Single-Node File Storage**: Uploaded images are stored on the local filesystem (`backend/uploads/`). For multi-instance, auto-scaling cloud deployments, plug in the provided `BaseStorageService` with an AWS S3 or Google Cloud Storage provider.
3. **In-App Real-Time Push**: Status updates sync upon user refresh or navigation; WebSocket push notifications can be added for instantaneous updates across browser sessions.
