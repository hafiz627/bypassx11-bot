# Architecture

- Frontend: React + Vite + TypeScript + Framer Motion.
- Backend: FastAPI + SQLModel + provider-oriented resolver engine.
- Provider system: one class per provider; fallback generic handler.
- Queue/parallelism: async gather for batch resolution with retry.
- Storage: SQLite history table (extensible to PostgreSQL).
