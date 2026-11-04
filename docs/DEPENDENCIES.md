# Dependencies

## Tools needed on your computer

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12 | Backend |
| Node.js | 22 LTS (20.9+ works) | Frontend |
| npm | comes with Node.js | Frontend packages |
| Git | any recent | Source control and deploys |
| Docker Desktop | optional | Local PostgreSQL/Redis, testing the production images |

## Backend (`backend/requirements.txt`)

| Package | Version | Why it is used |
|---|---|---|
| Django | 5.2.18 (LTS) | Web framework and the admin portal (CMS) |
| djangorestframework | 3.18.3 | REST API |
| drf-spectacular | 0.30.0 | API documentation (`/api/docs/` in development) |
| django-cors-headers | 4.9.0 | Cross-origin settings (only needed if the site and API use different domains) |
| django-environ | 0.14.0 | Reads settings from environment variables / `.env` |
| django-simple-history | 3.13.0 | Change history for medicines and invoices (who changed what) |
| django-otp | 1.7.5 | Two-factor (authenticator app) login for the admin |
| psycopg[binary] | 3.3.6 | PostgreSQL driver |
| celery | 5.6.3 | Background jobs: sending emails, building PDFs, retries |
| redis | 8.1.0 | Python client for the Redis queue |
| gunicorn | 26.2.0 | Production web server |
| whitenoise | 6.12.0 | Serves the admin's CSS/JS from Django |
| django-storages[s3] | 1.14.6 | Stores invoice PDFs in Amazon S3 |
| boto3 | 1.43.121 | AWS SDK used by django-storages |
| weasyprint | 70.0 | Turns the invoice HTML into a PDF |
| requests | 2.34.2 | Verifies the CAPTCHA token with Cloudflare |

System libraries for WeasyPrint (installed in `backend/Dockerfile`; on your own Linux/WSL machine run `sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0`).

## Frontend (`frontend/package.json`)

Runtime:

| Package | Version | Why |
|---|---|---|
| next | 16.3.4 | Framework (server rendering for SEO) |
| react, react-dom | 19.2.8 | UI library |
| framer-motion | ^13.2.0 | Animations in your design |
| lucide-react | ^1.42.0 | Icons |
| @fontsource/ibm-plex-sans | ^5.3.0 | Self-hosted body font (no Google Fonts request) |
| @fontsource/source-serif-4 | ^5.3.0 | Self-hosted heading font |

Development / build:

| Package | Version | Why |
|---|---|---|
| tailwindcss | ^4 | Styling |
| @tailwindcss/postcss | ^4 | Tailwind build plugin |

No extra packages were added for the catalogue; it uses the built-in `fetch`.

## Services and container images (production)

| Item | Version | Role |
|---|---|---|
| PostgreSQL | 16 (`postgres:16-alpine`) | Database |
| Redis | 7 (`redis:7-alpine`) | Job queue |
| Caddy | 2 (`caddy:2-alpine`) | HTTPS (automatic certificates) and routing |
| Node base image | `node:22-alpine` | Builds and runs the frontend |
| Python base image | `python:3.12-slim-bookworm` | Runs the backend |
| Ubuntu on the server | 24.04 LTS (ARM64) | Host operating system |
| Docker Engine + Compose plugin | current | Runs all containers |
| AWS CLI v2 | current | Uploads database backups to S3 |

## External accounts (free unless noted)

AWS account (pay as you go), domain registrar (client owns the domain), Google Workspace mailbox for sending email (paid per user), GitHub (private repository), Cloudflare Turnstile (optional CAPTCHA), Google Search Console and Google Business Profile.
