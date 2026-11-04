# Suremedra Platform (Phase 1)

Corporate website, medicine catalogue, enquiry flow and invoicing for Suremedra Enterprises.

| Part | Technology | Folder |
|---|---|---|
| Public website and catalogue | Next.js 16 (React 19), Tailwind CSS 4 | `frontend/` |
| Admin portal (CMS), API, background jobs | Django 5.2, Django REST Framework, Celery | `backend/` |
| Server setup, Docker, backups | Docker Compose, Caddy, shell scripts | `deploy/`, `docker-compose.*.yml` |
| Guides | Dependencies, AWS setup, day-to-day operations | `docs/` |

## What Phase 1 does

1. Admins add medicines in the admin portal (`/admin/`): brand, distributor, compositions with strengths, medicine type (tablet, capsule, syrup, injection...), pack size, HSN code and GST rate. A CSV import handles the first ~4,000 rows.
2. The public site (`/catalogue`) shows **only compositions, strength and type**, with search (typo tolerant on PostgreSQL) and filters. Brand, distributor and prices are never sent to the public.
3. A buyer adds medicines to an **enquiry list** and asks about availability (no login needed).
4. Admins and Super Admins are notified **in the admin portal and by email**; the buyer gets an acknowledgment with a reference number such as `ENQ-2026-0042`.
5. The admin records availability, quantity, the actual product (brand and distributor) and price per line, then clicks **Generate invoice**. A PDF proforma invoice is created and emailed to the buyer.

## Folder structure

```
backend/
  config/        settings, URLs, Celery
  core/          logging, request-id middleware, email queue + log, sequences, roles command
  catalog/       medicines, brands, distributors, compositions, public API, CSV import
  enquiries/     enquiries, notifications, public enquiry API, admin panel
  billing/       invoices, PDF template, numbering, admin
  templates/     Django Admin template overrides
  sample_data/   medicines_sample.csv
frontend/
  app/           pages: home, about, certifications, contact, catalogue, enquiry
  components/    Header, Footer, enquiry basket, forms
  lib/           API helpers
  content/       static company text (from your original design)
deploy/          Caddyfile, setup-server.sh, deploy.sh, backup.sh, restore.sh
docs/            DEPENDENCIES.md, AWS_SETUP.md, OPERATIONS.md
```

## Run it on your computer

You need: **Python 3.12**, **Node.js 22** (20.9 or newer works), and Git. Docker is optional.
Windows users: use **WSL2** (Ubuntu) for the backend. Invoice PDFs need Linux libraries that are awkward on plain Windows.

### 1. Backend (Terminal 1)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate            # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp .env.example .env                # default settings work as they are (SQLite, emails printed in the terminal)
python manage.py migrate
python manage.py setup_roles         # creates the "Admin" and "SuperAdmin" groups
python manage.py createsuperuser     # your login for /admin/
python manage.py import_medicines sample_data/medicines_sample.csv
python manage.py runserver 8000
```

Admin portal: http://localhost:8000/admin/  |  API docs (dev only): http://localhost:8000/api/docs/

With no `DATABASE_URL` the app uses a local SQLite file, and with no `REDIS_URL` background jobs run immediately inside the request. That is perfect for development. Search is typo-tolerant only on PostgreSQL (see "Optional: PostgreSQL and Redis" below).

### 2. Frontend (Terminal 2)

```bash
cd frontend
cp .env.example .env.example.local
npm install
npm run dev
```

Website: http://localhost:3000 (the catalogue is at `/catalogue`). In development Next.js forwards `/api/*` to Django on port 8000.

### 3. Try the whole flow

1. Open http://localhost:3000/catalogue, search `paracetamol`, click **Add to enquiry** on a result.
2. Click **Enquiry list**, fill in your details, submit. You get a reference number.
3. In the **backend terminal** you see the log lines and the emails (admin alert and buyer acknowledgment).
4. Open http://localhost:8000/admin/, log in. The dashboard shows the new enquiry notification. Open the enquiry.
5. For each line set **Availability = Available**, pick the **Medicine** (brand/distributor) and enter a **Unit price**. Save.
6. Click **Generate invoice** (top right), review the preview, and issue it. The PDF is saved under `backend/media/invoices/` and the email appears in the terminal.

### Optional: PostgreSQL and Redis locally

```bash
docker compose -f docker-compose.dev.yml up -d          # starts PostgreSQL and Redis
```

In `backend/.env` uncomment:

```
DATABASE_URL=postgres://suremedra:suremedra@localhost:5432/suremedra
REDIS_URL=redis://localhost:6379/0
```

Then run `python manage.py migrate` again, start the API, and in a third terminal run the worker:

```bash
celery -A config worker --loglevel=info
```

### Tests

```bash
cd backend && python manage.py test            # 24 tests: formulation rules, public API privacy, enquiries, invoices, admin pages
cd frontend && npm run build                   # type/compile check and production build
```

## Logging (backend)

Every module uses the standard Python logger (`logger = logging.getLogger(__name__)`). Output goes to the console, and optionally to a rotating file `backend/logs/app.log` (`LOG_TO_FILE=true`, 10 MB x 5 files).

```
2026-10-29 15:35:36,563 INFO    [64caff289be7] enquiries.services: In-app notifications created for 2 user(s)
2026-10-29 15:35:36,568 INFO    [64caff289be7] core.emailing: Email queued: id=6 kind=enquiry_ack to=a***@example.com
2026-10-29 15:35:36,630 INFO    [64caff289be7] core.request: POST /api/v1/public/enquiries -> 201 210.6ms ip=127.0.0.1 user=anonymous
```

* The value in `[...]` is a **request id** shared by every line of one request (also returned in the `X-Request-ID` header). Search the logs for it to follow a request end to end.
* What is logged: one line per request, enquiry created, notifications created, every email queued / sent / failed (with retry attempts), invoice issued / voided / PDF stored, CSV imports, rejected CAPTCHA/honeypot/throttled requests, admin 2FA state, health-check failures, unhandled errors with stack traces.
* Email addresses are masked (`a***@example.com`) and no passwords or tokens are logged.
* `LOG_LEVEL` (DEBUG, INFO, WARNING...) and `LOG_FORMAT=json` (one JSON object per line, for log tools) are set in `.env`.
* On the server the logs go to Docker: `docker compose --env-file .env.prod -f docker-compose.prod.yml logs -f api worker` (see `docs/OPERATIONS.md`).

## Public API (no login)

| Method and path | Purpose |
|---|---|
| `GET /api/v1/public/formulations?q=&type=&composition=&page=` | Search / filter the catalogue |
| `GET /api/v1/public/formulations/{slug}` | One listing |
| `GET /api/v1/public/filters` | Medicine types with counts |
| `GET /api/v1/public/compositions?q=` | Composition autocomplete |
| `POST /api/v1/public/enquiries` | Submit an enquiry (rate limited, CAPTCHA optional, honeypot, idempotency key) |
| `GET /api/health` | Health check (used by Docker and uptime monitors) |

The CMS API (`/api/v1/cms/`) is reserved for Phase 2. In Phase 1 the CMS is Django Admin.

## Important settings

All settings are environment variables. See `backend/.env.example`, `frontend/.env.example` and `.env.prod.example`.

| Setting | Meaning |
|---|---|
| `DJANGO_SECRET_KEY` | Long random secret. Required when `DJANGO_DEBUG=false` |
| `DATABASE_URL` | `postgres://user:pass@host:5432/db` (SQLite if empty) |
| `REDIS_URL` | Job queue. Empty = run jobs inline (dev only) |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | SMTP login (Gmail/Workspace now, SES later: only these values change) |
| `ADMIN_NOTIFICATION_EMAILS` | Extra addresses for new-enquiry alerts |
| `ADMIN_2FA` | `true` forces a one-time code at admin login (enable after setting up your device, see `docs/OPERATIONS.md`) |
| `AWS_STORAGE_BUCKET_NAME` | Store invoice PDFs in S3 instead of local disk |
| `TURNSTILE_SECRET_KEY` and `NEXT_PUBLIC_TURNSTILE_SITE_KEY` | Free CAPTCHA on the enquiry form (optional) |
| `NEXT_PUBLIC_SITE_URL` | Public website address, used in canonical URLs and the sitemap |

## Before going live

* Replace placeholder content in `frontend/content/site.js` (phone, second director, certifications) and the legal pages.
* Set the company details for invoices (`COMPANY_*`, especially `COMPANY_GSTIN`) and confirm with the company's chartered accountant that a **proforma invoice** is acceptable, and how GST/export (LUT) should be shown.
* Turn on `ADMIN_2FA`, set a real `DJANGO_SECRET_KEY`, and follow `docs/AWS_SETUP.md`.
* Add real description text to the main formulations in the admin (Formulations). Pages with no description can be marked non-indexable to avoid thin content.

## Docs

* `docs/DEPENDENCIES.md` - every dependency for the backend and frontend
* `docs/AWS_SETUP.md` - step-by-step AWS setup and first deployment (beginner friendly)
* `docs/OPERATIONS.md` - logs, backups and restore, updates, admin tasks, troubleshooting
