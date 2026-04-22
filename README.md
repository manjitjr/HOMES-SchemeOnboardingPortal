# HOMES Schemes Onboarding Portal

A web application for managing the onboarding of government schemes into the **HOMES** (Household Means-Testing & Eligibility System) platform. Converted from OutSystems to Python/FastAPI.

---

## What This Application Does

Government agencies (MOH, MSE, HDB, etc.) use this portal to configure their schemes for integration with HOMES. Each scheme must fill in 6 setup tabs — matching the official **"09. Scheme Set-up v1.7.xlsx"** form — and go through a 3-stage approval workflow before going live.

In addition, scheme users can register interest in onboarding calendar slots. Approvers/reviewers can view these interests as notifications.

### 6 Setup Tabs (matching the Excel form)

| Tab | Purpose |
|-----|---------|
| **1. Scheme Overview** | Agency info, scheme name/code, legislated vs consent, background details |
| **2. MT Parameters** | Means-test configuration — beneficiary/applicant setup, 5 MTC types (Related, Nuclear, Parent-Guardian, IFM, Free-form), income components, property |
| **3. Transaction Details** | How the scheme connects to HOMES — portal access, SFTP/API interfaces, load volumes, monthly breakdowns |
| **4. HOMES Functions** | MTC viewing permissions, MT result sharing, scheme affiliations, event trigger subscriptions (EV001-EV014), auto-MT |
| **5. MT Bands** | Subsidy band configuration — income/AV ranges, ID types, effective dates, near-margin buffers, ranking |
| **6. API & Batch Interfaces** | 20 API interfaces (P12-API1 to P20-API), 19 batch interfaces (P13-Batch1 to P20-Batch), 7 SFTP setups |

### Approval Workflow

```
Scheme User (create/edit) --> Approver (review + approve/reject) --> Final Approver (final approve/reject)
                          <-- reject with comments              <-- reject with comments
```

- **Change tracking**: Every edit is logged with before/after diffs
- **Comments**: Users can add comments at each approval stage
- **Reject flow**: Rejected schemes return to the previous stage with comments explaining why

### User Roles & Access Control

| Role | Permissions |
|------|-------------|
| **scheme_user** | Create and edit schemes for their own agency |
| **approver** | Review, comment, approve or reject schemes for their agency |
| **final_approver** | Final approval across all agencies, sees all records |
| **admin** | Manage users/roles via the admin portal, sees all records |

- Users belong to an **agency** (e.g. MOH, MSE) and can only see their own agency's schemes
- Users with `final_approver` or `admin` roles can see **all** schemes across agencies
- Users can have **multiple roles** (e.g. both scheme_user and approver)

### AI Tooltips

Each form field has an info icon with guidance text pulled from the original Excel form notes, helping users understand what to fill in.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy (async), Pydantic |
| **Database** | SQLite (dev) / PostgreSQL on Neon (production) |
| **Auth** | JWT tokens (PyJWT) |
| **Frontend** | Single HTML file, Tailwind CSS, Font Awesome, vanilla JavaScript |
| **Export** | Excel export via openpyxl |

---

## Project Structure

See `FRONTEND_BACKEND_FILE_MAP.md` for the latest frontend/backend ownership map.

```
app/
├── main.py                 # FastAPI app entry point, startup (table creation + user seeding)
├── config.py               # Database connection config (DATABASE_URL env var)
├── models.py               # SQLAlchemy models (includes scheduling tables)
├── auth.py                 # JWT auth, login, user management endpoints
├── routers/
│   └── schemes.py          # All scheme CRUD, workflow, comments, changes, export endpoints
│   └── scheduling.py       # Onboarding slot listing, interest registration, reviewer notifications
├── services/               # backend domain services (schemes, scheduling, guidance)
├── static/
│   └── index.html          # Complete frontend SPA (login, 6 tabs, approval, user management)
└── requirements.txt        # Python dependencies
Dockerfile                  # Container build
.dockerignore               # Excludes for Docker build
```

---

## Database Models (10 tables)

| Table | Purpose |
|-------|---------|
| `users` | User accounts with roles (JSON array), agency, active status |
| `scheme_overview` | Core scheme info (agency, name, code, consent, background) |
| `scheme_submissions` | Submission record with status, version, creator |
| `scheme_mt_parameters` | Tab 2 data as JSON blob |
| `transaction_details` | Tab 3 data as JSON blob |
| `homes_functions` | Tab 4 data as JSON blob |
| `mt_bands` | Tab 5 data as JSON blob |
| `api_batch_interfaces` | Tab 6 data as JSON blob |
| `change_log` | Audit trail of all field changes |
| `comments` | Comments per submission with stage and user |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login, returns JWT token |
| GET | `/api/auth/me` | Current user info |
| GET | `/api/auth/users` | List all users (admin only) |
| POST | `/api/auth/users` | Create user (admin only) |
| PUT | `/api/auth/users/{id}` | Update user roles/agency (admin only) |

### Schemes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/schemes` | List schemes (agency-filtered) |
| POST | `/api/schemes` | Create new scheme |
| GET | `/api/schemes/{id}` | Get full scheme with all tab data |
| PUT | `/api/schemes/{id}` | Update scheme overview |
| PUT | `/api/schemes/{id}/tab/{tab}` | Update tab data (mt_parameters, transactions, homes_functions, mt_bands, api_interfaces) |

### Workflow
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/schemes/{id}/submit` | Submit for approval |
| POST | `/api/schemes/{id}/approve` | Approver approves |
| POST | `/api/schemes/{id}/final-approve` | Final approver approves |
| POST | `/api/schemes/{id}/reject` | Reject with comment |

### Comments, Changes & Export
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/schemes/{id}/comments` | List comments |
| POST | `/api/schemes/{id}/comments` | Add comment |
| GET | `/api/schemes/{id}/changes` | View change log |
| GET | `/api/schemes/{id}/export` | Download as Excel |

### Onboarding Scheduling
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scheduling/slots` | List available onboarding slots (with interest counts) |
| POST | `/api/scheduling/slots/{slot_id}/interest` | Scheme user marks slot as interested |
| GET | `/api/scheduling/notifications` | Approver/reviewer notification feed of interests |

---

## Getting Started

### Option 1: Run Locally

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r app/requirements.txt

# 3. Start the server (uses SQLite by default)
uvicorn app.main:app --reload --port 8000

# 4. Open browser
open http://localhost:8000
```

### Option 2: Run with Docker

```bash
# Build
docker build -t homes-onboarding .

# Run
docker run -p 8000:8000 homes-onboarding

# Open browser
open http://localhost:8000
```

### Option 3: Deploy to Railway

#### Step 1: Prepare a Git Repo

```bash
# Initialize git in the project folder
cd scheme-onboarding
git init
git add app/ Dockerfile .dockerignore README.md
git commit -m "Initial commit - HOMES Onboarding Portal"

# Push to GitHub (create a repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/homes-onboarding.git
git branch -M main
git push -u origin main
```

#### Step 2: Create Railway Project

1. Go to [https://railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your `homes-onboarding` repo
4. Railway will auto-detect the Dockerfile and start building

#### Step 3: Add Neon PostgreSQL Database

1. In your Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
   - OR use an external Neon database:
     - Go to [https://neon.tech](https://neon.tech), create a free database
     - Copy the connection string from the Neon dashboard

2. In Railway, go to your service → **"Variables"** tab → **"New Variable"**:
   ```
   DATABASE_URL=postgresql+asyncpg://user:pass@your-host.neon.tech/dbname?sslmode=require
   ```
   - If using Railway's built-in PostgreSQL, reference the variable:
   ```
   DATABASE_URL=postgresql+asyncpg://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}
   ```

#### Step 4: Configure Port

Add another variable in Railway:
```
PORT=8000
```

Railway exposes your app on a public URL automatically (e.g. `https://homes-onboarding-production.up.railway.app`).

#### Step 5: Verify Deployment

1. Click the generated Railway URL
2. You should see the HOMES login page
3. Login with `admin` / `password`
4. Tables are auto-created and demo users are seeded on first startup

#### Updating After Changes

```bash
git add -A
git commit -m "Description of changes"
git push origin main
```
Railway auto-deploys on every push to `main`.

---

### Option 4: Deploy to Render

1. Push to GitHub (same as Step 1 above)
2. Go to [https://render.com](https://render.com) → **"New Web Service"**
3. Connect your repo
4. Set:
   - **Build Command**: `pip install -r app/requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variable: `DATABASE_URL` = your Neon connection string
6. Deploy

---

## Switching to PostgreSQL (Neon)

Edit `app/config.py` or set the `DATABASE_URL` environment variable:

```
DATABASE_URL=postgresql+asyncpg://user:pass@your-host.neon.tech/dbname?sslmode=require
```

Make sure `asyncpg` is installed (it's already in requirements.txt).

---

## Demo Accounts

The app automatically seeds these demo users on first startup:

| Username | Password | Agency | Roles |
|----------|----------|--------|-------|
| `moh_user` | password | MOH | scheme_user |
| `moh_approver` | password | MOH | approver |
| `mse_user` | password | MSE | scheme_user |
| `mse_approver` | password | MSE | approver |
| `admin` | password | HOMES | final_approver, admin |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./homes_onboarding.db` | Database connection string |

---

## Original Source

Converted from OutSystems OML files and the official Excel form:
- `HOMES Schemes Onboarding.oml` (main module)
- `09. Scheme Set-up v1.7.xlsx` (field definitions)
