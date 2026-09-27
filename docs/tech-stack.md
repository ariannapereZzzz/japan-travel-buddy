# Tech stack

Japan Travel Buddy uses the same application stack as DoctorDesk (`kame-desk`). Product code is a trip manager, not a clinic.

| Layer                  | Choice                                        |
| ---------------------- | --------------------------------------------- |
| Monorepo               | pnpm workspaces + Turborepo                   |
| Frontend               | React 19 + TanStack Start + Vite + TypeScript |
| Server state           | TanStack Query                                |
| Styling                | Tailwind CSS                                  |
| Validation             | Zod (web) + Pydantic v2 (API)                 |
| Backend                | FastAPI, always-on                            |
| API contract           | REST `/api/v1` + OpenAPI                      |
| ORM / migrations       | SQLAlchemy 2 (async) + Alembic                |
| Database               | PostgreSQL 16 (`pgvector/pgvector` image)     |
| Jobs / cache           | Redis + ARQ                                   |
| Files (local stand-in) | MinIO (S3-compatible, Cloudflare R2 later)    |
| Email (local stand-in) | Mailhog                                       |
| Python tooling         | uv                                            |

## Local ports

Offset from DoctorDesk so both projects can run together.

| Service  | URL                                             |
| -------- | ----------------------------------------------- |
| Web      | http://localhost:3200                           |
| API      | http://localhost:8200                           |
| Postgres | `localhost:5433`                                |
| Redis    | `localhost:6380`                                |
| MinIO    | API `localhost:9010`, console `localhost:9011`  |
| Mailhog  | SMTP `localhost:1026`, UI http://localhost:8026 |

## Layout

| Path                  | Role                                                                          |
| --------------------- | ----------------------------------------------------------------------------- |
| `apps/web`            | TanStack Start UI                                                             |
| `apps/api`            | FastAPI, owns trip data and saved progress                                    |
| `packages/api-client` | Orval config. Generate after `pnpm --filter @japan-travel/api openapi:export` |

Clinic auth, RBAC, WebSockets, and the AI assistant are not part of this app. The HTML prototype is a single traveler, and the API stores that traveler's checks, shopping list, and expenses.
