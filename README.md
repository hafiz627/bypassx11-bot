# Universal URL Resolver (Safe, Extensible Scaffold)

> This project provides a production-style, extensible **URL resolution platform scaffold** with a modern web UI and FastAPI backend.
> It is intentionally implemented for **safe, legitimate link resolution** (redirect expansion, metadata inspection, provider adapters) and does **not** include evasion/circumvention of access controls (e.g., CAPTCHA solving, Cloudflare bypass, or defeating protected pages).

## Monorepo Structure

```
.
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  │  ├─ bypass.py
│  │  │  ├─ history.py
│  │  │  ├─ providers.py
│  │  │  └─ status.py
│  │  ├─ core/
│  │  │  ├─ config.py
│  │  │  ├─ rate_limit.py
│  │  │  └─ security.py
│  │  ├─ engine/
│  │  │  ├─ manager.py
│  │  │  ├─ strategies.py
│  │  │  └─ providers/
│  │  │     ├─ base.py
│  │  │     ├─ generic.py
│  │  │     └─ tinyurl.py
│  │  ├─ models/
│  │  │  ├─ history.py
│  │  │  └─ provider.py
│  │  ├─ schemas/
│  │  │  ├─ api.py
│  │  │  └─ common.py
│  │  ├─ db.py
│  │  └─ main.py
│  ├─ requirements.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  │  ├─ UrlInput.tsx
│  │  │  ├─ ResultCard.tsx
│  │  │  └─ Header.tsx
│  │  ├─ lib/api.ts
│  │  ├─ App.tsx
│  │  ├─ main.tsx
│  │  └─ styles.css
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ vite.config.ts
│  └─ Dockerfile
├─ docker-compose.yml
├─ .env.example
└─ docs/
   ├─ ARCHITECTURE.md
   └─ DEPLOYMENT.md
```

## Features Included

- Modern responsive glassmorphism UI (React + Tailwind-like utility styling approach in CSS, Framer Motion, dark mode).
- Batch URL intake, paste detection, drag-and-drop input, provider detection, and local history/favorites.
- FastAPI backend with:
  - `/api/bypass`
  - `/api/status`
  - `/api/history`
  - `/api/providers`
- Safe resolution engine:
  - Redirect tracing
  - Header and content-type inspection
  - DOM parsing for obvious canonical links
  - Recursive resolution with bounded depth
  - Parallel batch processing and retries
- Security guardrails:
  - Input sanitization
  - Basic rate limiting
  - CORS allow-list
  - Security headers

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## Environment

Copy and edit:

```bash
cp .env.example .env
```

## API Examples

### POST /api/bypass

```json
{
  "urls": ["https://tinyurl.com/2p8x7wzv"],
  "follow_redirects": true,
  "max_depth": 8
}
```

## Extending Providers

Add a new adapter in `backend/app/engine/providers/` implementing `ProviderHandler` and register it in `manager.py`.

## Note on Compliance

This scaffold is designed for lawful URL resolution and observability workflows. Do not use it to circumvent third-party protections, authentication gates, anti-bot checks, or legal restrictions.
