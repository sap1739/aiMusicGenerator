# Architecture

```mermaid
flowchart LR
  U[Creator] --> W[Next.js Web]
  W -->|REST + polling| A[FastAPI]
  A --> P[Policy + Consent]
  A --> J[Async Job Runner]
  A --> D[(SQLite / Postgres-ready repository)]
  A --> S[Local / S3-ready storage]
  J --> E{Engine adapter}
  E --> M[Deterministic demo engine]
  E --> ACE[ACE-Step 1.5 REST server]
  ACE --> GPU[Local or hosted GPU]
  J --> F[FFmpeg / audio analysis]
```

The product and inference runtime are deliberately separate. Auralis owns validation, consent, jobs, persistence, and UX. ACE-Step owns inference behind its published REST server. This minimizes copied code, makes model upgrades safer, and permits a hosted worker later without rewriting the app.

The in-process runner is suitable for an MVP and exposes the same job contract a Redis/RQ or Celery worker would use. Storage and repository interfaces are kept behind service modules so S3 and Postgres can replace local defaults.
