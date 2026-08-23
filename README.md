# Hire — Advanced Job Searching Platform

A full-stack job platform with four roles — **Job Seeker, Enterprise (Recruiter), Institute, Admin** —
built on **Plan B**: React + Tailwind web frontend, FastAPI (Python) backend, Supabase/Postgres database.

This is a **runnable foundation**. The core architecture and the three emphasized flows are
implemented end-to-end and tested. The remaining CRUD screens are wired to real API endpoints
with the correct fields, ready for you to extend.

---

## What works today

**The three emphasized flows are fully implemented and tested:**

1. **Institute Excel upload → auto-resume → emailed credentials.**
   An institute uploads an `.xlsx` describing 1..N students. For each row the backend maps the
   available columns (flexible header matching), auto-builds a resume, stores it, generates a
   random password, creates the login, and emails each student their user ID + password.
   → `backend/app/resume_service.py`, `POST /api/institute/upload`

2. **Job seeker edits resume + switches template.**
   The job seeker can add additional information and edit any resume field, and switch between
   **six professional templates** — Classic (ATS-safe serif), Modern (navy sidebar), Professional
   (banner header + timeline), Executive (monogram), Minimal, and Compact. The template gallery
   shows a live scaled preview of each one rendered with the seeker's real data, with full-size
   preview and A4 print/download.
   → `frontend/src/pages/jobseeker/`, `PUT /api/jobseeker/profile`, `PUT /api/jobseeker/template`

3. **Job seeker sees who viewed their application + live status.**
   When a recruiter views or downloads a resume it's recorded; the seeker sees the company,
   recruiter and action under "Recruiter views", and the live status of each application
   (Applied → Under Review → Shortlisted → Rejected → Selected) under "Applied jobs".
   → `ProfileView` model, `GET /api/jobseeker/profile-views`, `GET /api/jobseeker/applications`

**Also implemented:** JWT auth for all four roles, a modern branded UI with your logo, home page
with header logins (no awkward middle cards), self-registration (job seeker + enterprise), admin
CRUD for institutes/enterprises/seekers with emailed credentials and password reset, enterprise
resume search + job posting + applications inbox with status control + banner posting, institute
student search + job posting, real-time **chat with block controls** between seekers and recruiters,
**live-updating** stats/statuses/badges, and an **email diagnostics** panel for Gmail setup.

---

## Run it locally

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # defaults run on SQLite, emails print to console
python seed.py                     # creates demo accounts
uvicorn app.main:app --reload      # http://localhost:8000  (docs at /docs)
```

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173  (proxies /api to :8000)
```

**Before committing, run `npm run verify`.** `vite build` alone does *not* catch undefined
identifiers (bundlers treat unknown names as globals), so a missing import passes the build and
then blanks the page at runtime with `X is not defined`. `npm run verify` runs an ESLint
`no-undef` pass first, then the build, which catches exactly that.

### Demo logins (from `seed.py`)

| Role       | Email           | Password |
|------------|-----------------|----------|
| Admin      | admin@hire.com  | admin123 |
| Institute  | coco@hire.com   | inst123  |
| Enterprise | hr@campus.com   | ent123   |

Job-seeker accounts are created by uploading an Excel in the Institute portal (Data upload) —
the generated passwords appear in the results table **and** print to the backend console
(console email mode). Log in as one to see the resume/template/application flows.

---

## Database

Local dev runs on SQLite with zero setup. To move to Supabase Postgres, follow
**[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** — it's one line in `.env` plus a verification step.

Two commands worth knowing:

```bash
python check_db.py    # shows what you'll connect to, and names the fix if it fails
python seed.py        # creates tables, adds missing columns, seeds demo data
```

`seed.py` runs the schema migration automatically, so if you ever hit
`no such column: jobs.sector` after pulling an update, re-running `python seed.py`
repairs the database in place — on SQLite and on Supabase.

## Switch to Supabase (production database)

The backend uses plain SQLAlchemy, so moving from SQLite to Supabase's Postgres is one line.
In `backend/.env`:

```
DATABASE_URL=postgresql+psycopg2://postgres:YOUR-PASSWORD@db.YOUR-REF.supabase.co:5432/postgres
```

Get the string from **Supabase dashboard → Project Settings → Database → Connection string (URI)**.
Tables are created automatically on startup. For real schema management later, add Alembic migrations.

## Turn on real email (Gmail) — important

Gmail will **not** accept your normal password over SMTP. You must use an **App Password**:

1. Turn on **2-Step Verification** for the Google account.
2. Go to https://myaccount.google.com/apppasswords and create an app password for **Mail**
   (it's a 16-character code like `abcd efgh ijkl mnop` — remove the spaces).
3. In `backend/.env` set:
   ```
   EMAIL_ENABLED=True
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=youraddress@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop     # the app password, no spaces
   EMAIL_FROM=youraddress@gmail.com   # must match SMTP_USER for Gmail
   ```
4. Restart the backend.

**Test it without hunting through logs:** log in as admin and open **Reports → Email diagnostics**,
enter your address and click *Send test*. It shows the exact error if auth fails (that panel calls
`POST /api/health/email-test`). Until `EMAIL_ENABLED=True`, every email prints to the backend
console so you can still develop the credential flows.

Common causes of "no email": `EMAIL_ENABLED` left as `False`, using the Google account password
instead of an App Password, or 2-Step Verification not enabled (App Passwords require it).

## v2 features

**Notifications & job alerts** — an in-app bell (live-polled) fires on four events: a recruiter
views/downloads your profile, an application status changes, a new message arrives, and a newly
posted job matches your skills. Job alerts also send an email. See `app/notify_service.py`.

**Job recommendations with match scoring** — every active job is scored 0–100 against the seeker's
skills (70%), location (15%) and education (15%), with the matching skills listed. Powers both the
"Recommended" page and the "Top matches" panel on the dashboard.

**Saved jobs** — bookmark from search or recommendations; one endpoint toggles save/unsave.

**Role dashboards with charts** — job seekers get an applications-by-status bar chart, a profile
completeness donut with a list of what's missing, and top matches. Recruiters get a hiring-pipeline
chart plus jobs/applications/resumes-viewed counters. Charts are plain SVG/CSS — no chart library.

**Image uploads** — profile photos and company/institute logos (PNG/JPG/WEBP, max 2 MB). Files are
stored under `backend/uploads` and served at `/uploads/...`. To move to Supabase Storage, replace
`_store()` in `app/routers/uploads.py` — nothing else depends on where the bytes live.

**Forgot / reset password** — self-service flow with a single-use, 1-hour token emailed to the user.
The endpoint returns the same response whether or not the email exists, so it can't be used to
enumerate accounts.

**Manage jobs** — recruiters can close/reopen postings and view the applicant list per job.

## AI features (Groq)

Turn on in `backend/.env`:

```
AI_ENABLED=True
GROQ_API_KEY=gsk_your_key_here          # free key: https://console.groq.com/keys
GROQ_MODEL=openai/gpt-oss-20b           # must be a model YOUR key supports — see below
```

Restart the backend.

### Picking a valid model

**Groq retires model IDs over time**, so a name that worked last month can start returning
"model not found". Never trust a hardcoded name — read the list from your own key:

- **In the app:** log in as admin → **Reports → AI model check** → *Check my models*. It shows
  whether your configured model is valid and lists every model your key can use, with copy buttons.
- **From the API:** `GET /api/ai/models`
- **From a terminal:**
  ```bash
  curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models
  ```

Paste a valid ID into `GROQ_MODEL` and restart. If a model disappears later, the error message
names the problem and points you at this check rather than failing silently. AI buttons appear automatically once `/api/ai/status` reports enabled —
**with AI off the whole app still works**, the buttons simply don't render.

**For job seekers**
- *Write with AI* — drafts a career objective from your own details, with improvement tips.
- *Suggest with AI* (skills) — proposes skills based on your education and current skills.
- *Import from existing resume* — paste your old resume; AI fills every field for review.
- *Why this fits* — per job: strengths, gaps, and an application tip, alongside the match score.
- *Interview prep* — six likely questions with answer hints, plus questions to ask them.
- *Smart search* — type "fresher mechanical jobs in Hyderabad with CAD" and it becomes filters.

**For recruiters and institutes**
- *Draft with AI* — turns a job title plus a few fields into a full posting (description,
  requirements, responsibilities, skills), which you edit before posting.
- *Brief* — an AI screening summary of any candidate: strengths, gaps, screening questions.

**Safety and cost notes.** Prompts instruct the model never to invent qualifications the user
didn't provide, and the recruiter-facing prompts forbid speculation about protected attributes.
Every AI call is user-initiated (no background calls), so cost scales with clicks, not traffic.
All AI output is presented as a *suggestion* the user must accept — nothing is saved automatically.

If a call fails you get a specific message (bad key, unknown model, rate limit, network) rather
than a silent failure. Model names change; if you see "model not found", update `GROQ_MODEL`.

## Premium UI

Login pages use a split layout with an animated aurora brand panel, role selector cards,
floating-label inputs, and per-role copy. Forms across the app use searchable comboboxes
(type to filter, free text allowed, optional AI suggestions) and tag inputs for multi-value
fields like skills and languages. Motion respects `prefers-reduced-motion`.

## Chat & safety

Job seekers and recruiters can message each other in real time:
- Recruiters start a chat from **Applications** or **Resume search** (Message button).
- Job seekers start a chat from **Recruiter views** (companies that viewed them).
- Either side can **block** the other; a blocked sender is refused with a clear message.
- Unread counts drive the live badge in the sidebar/header (polled every few seconds).

Endpoints live in `backend/app/routers/chat.py`; the shared UI is `frontend/src/components/Chat.jsx`.
This is polling-based for simplicity and reliability — swap to WebSockets later if you want instant push.

## Live updates

Dashboard stats, applied-job statuses, recruiter-view lists, the applications inbox and the message
badges all refresh on a short interval, so "resume seen", "job posted" and new messages appear without
a manual reload.

---

## Project structure

```
hire/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app + routers + CORS
│   │   ├── config.py          settings (DATABASE_URL, JWT, email)
│   │   ├── database.py        SQLAlchemy engine/session
│   │   ├── models.py          all tables (User, Institute, Enterprise, JobSeeker, Job,
│   │   │                       Application, ProfileView, Banner)
│   │   ├── schemas.py         Pydantic request/response models
│   │   ├── auth.py            bcrypt hashing, JWT, role guards
│   │   ├── email_utils.py     email sending (console fallback)
│   │   ├── resume_service.py  Excel → resume + credentials (emphasized flow)
│   │   └── routers/           auth, admin, enterprise, institute, jobseeker, public
│   ├── seed.py                demo data
│   └── requirements.txt
└── frontend/
    └── src/
        ├── App.jsx            routes + role guards
        ├── lib/api.js         fetch wrapper with JWT
        ├── context/AuthContext.jsx
        ├── components/ui.jsx  Toast, ProtectedRoute, DashboardLayout, StatusBadge
        └── pages/
            ├── Home.jsx, Login.jsx, Misc.jsx
            ├── jobseeker/     JobSeeker.jsx (dashboard) + ResumeView.jsx (3 templates)
            ├── enterprise/    Enterprise.jsx
            ├── institute/     Institute.jsx (incl. Data upload)
            └── admin/         Admin.jsx
```

---

## How to extend (where to pick up)

- **Logo/photo uploads** → add a `POST /upload` that stores files in Supabase Storage; save the
  returned URL on `logo_url` / `profile_picture_url`.
- **Reports (SQL query form)** → the admin/enterprise "Reports" user story. Add a safe,
  parameterized query endpoint; the summary endpoint (`/api/admin/reports/summary`) is a start.
- **Job alerts / new-job counter** → the `dashboard` endpoints return `new_jobs`; wire a badge and
  a scheduled mailer.
- **GST/PAN verification** → fields exist on `Enterprise`; add a verification step at registration.
- **Resume PDF export** → currently uses browser print-to-PDF of the selected template; swap for a
  server-side PDF (e.g. WeasyPrint) if you need pixel-perfect files with attachments in emails.
- **Mobile app** → the FastAPI backend is shared. Build the React Native + Expo client against the
  same endpoints; credentials already work across web and mobile by design.

## Notes

- Colors are intentionally plain/neutral for now (per the brief) — styling lives in
  `frontend/src/index.css` and Tailwind classes, easy to rebrand with your blue/green palette.
- JSON columns (skills, education, experience) keep the schema portable across SQLite and Postgres.
  On Supabase you can later push resume search into JSONB queries for performance at scale.
