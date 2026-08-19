# Adventoria

A premium, dark-fantasy website for the **Adventoria** Minecraft server — "Where Every Adventure Begins."

Built with Next.js (App Router), TypeScript, Tailwind CSS v4, Framer Motion, Prisma + SQLite, and Auth.js (NextAuth v5).

## Getting Started

```bash
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000).

## Environment Variables

Configured in `.env` (already set up for local development):

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLite connection string (`file:./dev.db`) |
| `AUTH_SECRET` | NextAuth session signing secret — **replace in production** |
| `ADMIN_EMAIL` / `ADMIN_DEFAULT_PASSWORD` | Used only by the seed script to create the default admin |
| `NEXT_PUBLIC_SERVER_ADDRESS` | Minecraft server address shown site-wide and checked via mcsrvstat.us |

## Database

The app uses **Prisma + SQLite** for accounts only (email, gametag, hashed password, role, registration date). All other content (news, kingdoms, gallery, FAQ, quests, leaderboard, shop) is mock JSON in `src/data/`, ready to be swapped for a real API/CMS later.

```bash
npx prisma migrate dev   # apply schema changes
npx prisma db seed       # (re)creates the default admin account
npx prisma studio        # visually browse the database
```

### Default Administrator

Seeded automatically the first time you run `prisma db seed`:

- Email: `elhedadiadamelhedadi@gmail.com`
- Password: value of `ADMIN_DEFAULT_PASSWORD` in `.env` (`ChangeMe123!` by default)

**Change this password after first login in production.** Passwords are always stored bcrypt-hashed and are never displayed anywhere, including the admin dashboard.

## Connecting the Real Minecraft Server

Update `NEXT_PUBLIC_SERVER_ADDRESS` in `.env` to your real server address. The home page status widget (`src/lib/mcstatus.ts`) queries the public [mcsrvstat.us](https://mcsrvstat.us) API — no further code changes needed.

## Adding Microsoft/Xbox Login Later

The schema (`prisma/schema.prisma`) already includes Auth.js-compatible `Account`/`Session` models. To add Microsoft sign-in:

1. Register an app in Azure AD / Microsoft Entra ID.
2. Add a `MicrosoftEntraID` provider to the `providers` array in `src/lib/auth.ts`.
3. Add the `@auth/prisma-adapter` as the adapter in the same file.

## Project Structure

```
src/
  app/            Route segments (pages + API routes)
  components/     Reusable UI, layout, and page-section components
  data/           Mock JSON content (news, kingdoms, gallery, FAQ, etc.)
  lib/            Prisma client, auth config, validation, utilities
  types/          Shared TypeScript types
prisma/
  schema.prisma   Database schema (users, accounts, sessions)
  seed.ts         Default admin seeder
```

## Production Notes

- Set a strong, random `AUTH_SECRET` (e.g. `openssl rand -base64 32`).
- Change the default admin password immediately after first deploy.
- SQLite is fine for small-to-medium deployments; swap the Prisma datasource provider for Postgres/MySQL if you need concurrent write scaling later — no application code changes required beyond the schema's `datasource` block.
