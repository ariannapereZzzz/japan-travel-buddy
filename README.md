# Japan Travel Buddy

Trip manager for the Japan 2026 itinerary (Osaka, Kyoto, Tokyo, Kamikochi, Kawaguchiko). Same monorepo stack as DoctorDesk: pnpm, Turborepo, TanStack Start, FastAPI, Postgres, Redis.

## Run

```bash
pnpm install
cd apps/api && uv sync --all-extras && cd ../..
pnpm run dev
```

Web: http://localhost:3200  
API: http://localhost:8200/api/v1/health

`pnpm run dev` starts Postgres, Redis, MinIO, and Mailhog, applies migrations, seeds the trip, then starts the API, ARQ worker, and web app.

## Scripts

| Command                   | What it does                                                   |
| ------------------------- | -------------------------------------------------------------- |
| `pnpm run dev:docker`     | Infra only                                                     |
| `pnpm run db:migrate`     | Alembic upgrade (local Postgres)                               |
| `pnpm run db:seed`        | Load the Japan 2026 trip if it is missing                      |
| `pnpm run db:seed:force`  | Replace the seeded trip. Clears checks, shopping, and expenses |
| `pnpm run db:reset:local` | Drop the local database, migrate, seed                         |
| `pnpm run test`           | pytest + vitest                                                |

See `docs/tech-stack.md` for ports and how this maps to the DoctorDesk stack.
