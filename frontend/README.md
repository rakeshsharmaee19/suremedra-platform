# Suremedra website (frontend)

Next.js 16 app: corporate pages, medicine catalogue (server rendered for SEO) and the enquiry basket.
The catalogue reads from the Django API; see the root `README.md` for how to run both together.

```bash
cp .env.example .env.example.local
npm install
npm run dev        # http://localhost:3000  (expects the API on http://localhost:8000)
npm run build      # production build (standalone output, used by the Dockerfile)
```

Static company text lives in `content/site.js`. API helpers are in `lib/api.js`.
