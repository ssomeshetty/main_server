# Karnataka Politician Tracking System

An open-source, non-partisan civic transparency web platform tracking election affidavits, declared net worth, office tenures, and legal record disclosures for Karnataka's 224 State Assembly MLAs and 28 Lok Sabha MPs.

---

## 🏛️ Architecture Overview

- **Frontend**: Next.js 14 (App Router) with TailwindCSS, TypeScript, and i18n support (English & Kannada).
- **Backend**: Django 6.0 REST Framework API with PostgreSQL/MySQL support (defaults to SQLite for local development).
- **Caching & Throttling**: Redis Cache with Django REST Framework Scoped Rate Throttling.
- **Data Integrity**: 100% factual visual cards, verified ECI affidavit links, and strict legal neutrality ("Declared Legal Cases").

```
+------------------------------------+      HTTP / REST API      +------------------------------------+
|         Next.js 14 Frontend        | ------------------------> |         Django 6.0 REST API        |
|  (App Router / Client / Server)    |                           |  (ReadOnlyModeMiddleware / DRF)     |
+------------------------------------+                           +------------------------------------+
                                                                                  |
                                                                                  v
                                                                 +------------------------------------+
                                                                 |     SQLite / MySQL / Redis Cache   |
                                                                 +------------------------------------+
```

---

## 📋 Technical Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Database**: SQLite (built-in for dev) or MySQL 8.0+ / PostgreSQL (production)

---

## 🚀 Quick Setup (Fresh Machine / New Laptop)

You can set up the entire project on a new laptop in one step using the setup script:

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

---

## 🛠️ Manual Installation & Setup Guide

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Main_server
```

### 2. Backend Setup
```bash
# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r politicians_tracker/requirements.txt

# Copy example environment file
cp .env.example .env

# Run database migrations (creates SQLite tables and seeds public records)
USE_SQLITE=true DJANGO_SECRET_KEY=dev_secret_key python politicians_tracker/manage.py migrate

# (Optional) Run test suite to verify backend health
USE_SQLITE=true DJANGO_SECRET_KEY=dev_secret_key python politicians_tracker/manage.py test politicians_tracker.apps.core.tests

# Start Django Backend Server (Port 8000)
USE_SQLITE=true DJANGO_DEBUG=true DJANGO_SECRET_KEY=dev_secret_key python politicians_tracker/manage.py runserver 0.0.0.0:8000
```

### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm ci

# Copy example environment file
cp .env.example .env.local

# Verify TypeScript compilation
npx tsc --noEmit

# Start Next.js Development Server (Port 3000)
npm run dev
```

The application will be accessible at:
- **Frontend App**: `http://localhost:3000/en/politicians`
- **Backend API**: `http://localhost:8000/api/v1/politicians/`

---

## 🧪 Running Tests & Quality Checks

- **Backend Unit & Integration Tests (84 tests)**:
  ```bash
  USE_SQLITE=true DJANGO_SECRET_KEY=dev_secret_key python politicians_tracker/manage.py test politicians_tracker.apps.core.tests
  ```
- **Frontend Type Safety**:
  ```bash
  cd frontend && npx tsc --noEmit
  ```
- **Frontend Production Build**:
  ```bash
  cd frontend && npm run build
  ```

---

## ⚙️ Environment Variables Reference

### Backend Environment (`.env`):
- `DJANGO_SECRET_KEY`: Production secret key (fallback to dev key in DEBUG).
- `DJANGO_DEBUG`: Set to `True` for development, `False` for production.
- `USE_SQLITE`: Set to `true` to use SQLite file storage; `false` to use MySQL.
- `ADMIN_URL_PREFIX`: Secret path prefix for Django admin (e.g. `mgmt-admin`).

### Frontend Environment (`frontend/.env.local`):
- `NEXT_PUBLIC_API_URL`: Backend REST API base URL (`http://localhost:8000/api/v1`).

---

## 📁 Repository Structure

```
Main_server/
├── .env.example                 # Root backend environment template
├── .gitignore                    # Comprehensive Git ignore rules
├── README.md                     # Setup and architectural documentation
├── scripts/
│   └── setup.sh                  # Non-destructive local setup script
├── frontend/
│   ├── app/                      # Next.js App Router ([lang]/politicians/[id])
│   ├── components/               # React components (AnalyticsPanel.tsx)
│   ├── lib/                      # API client (api.ts)
│   ├── package.json              # Node dependencies
│   └── .env.example              # Frontend environment template
├── politicians_tracker/
│   ├── manage.py                 # Django CLI entrypoint
│   ├── settings.py               # Django configuration & rate limits
│   ├── urls.py                   # Global API routing
│   ├── requirements.txt          # Python dependencies
│   └── apps/core/                # Core DRF application (models, views, serializers)
│       ├── migrations/           # Database migrations 0001–0010
│       ├── management/commands/  # Seeding & enrichment management commands
│       └── tests/                # Automated test suite (84 tests)
```

---

## 🔒 Security & Privacy Notes

- **Read-Only API**: All public API endpoints are read-only (`GET`/`HEAD`/`OPTIONS`). Modifying HTTP verbs (`POST`, `PUT`, `DELETE`) are blocked with HTTP `405 Method Not Allowed`.
- **Public Affidavit Data**: All assets, election figures, and legal record summaries are parsed directly from sworn nomination affidavits filed with the Election Commission of India (ECI).
- **No Predictive Judgments**: The application presents verified public facts without predictive criminality scores, internal intelligence ratings, or subjective rankings.
