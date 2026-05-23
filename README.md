# PodCraft AI — Complete UI Design System

Vite + React 18 + TypeScript + Tailwind v4 + Supabase Auth.

## Quick start

```bash
pnpm install           # or npm i / yarn
cp .env.example .env.local
# fill in VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY
pnpm dev
```

App boots at http://localhost:5173.

## Scripts

| Command               | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `pnpm dev`            | Start Vite dev server                            |
| `pnpm build`          | Type-check + production build to `dist/`         |
| `pnpm preview`        | Serve the production build locally               |
| `pnpm type-check`     | TypeScript no-emit check                         |
| `pnpm lint`           | ESLint over `src/`                               |
| `pnpm lint:fix`       | ESLint with autofix                              |
| `pnpm format`         | Prettier write                                   |
| `pnpm format:check`   | Prettier verify                                  |
| `pnpm test`           | Run Vitest suite once                            |
| `pnpm test:watch`     | Vitest in watch mode                             |
| `pnpm test:coverage`  | Vitest coverage report                           |

## Project structure

```
src/
  app/
    App.tsx                  # ErrorBoundary + AuthProvider + RouterProvider
    routes.tsx               # Public + ProtectedRoute-wrapped routes
    providers/
      auth-provider.tsx      # Supabase session context + useAuth() hook
    components/
      error-boundary.tsx     # Global error UI
      protected-route.tsx    # Auth gate for private pages
      ...                    # Layout, glass-card, ui/* (shadcn)
    pages/                   # Page components, including not-found-page
  lib/
    supabase.ts              # Single Supabase client (reads VITE_* env)
  styles/                    # Tailwind, theme, fonts
  test/                      # Vitest setup + sample tests
  vite-env.d.ts              # Typed import.meta.env
public/
  favicon.svg
  robots.txt
  manifest.webmanifest
```

## Environment variables

All client-side vars **must** be prefixed `VITE_`. See `.env.example` for the
full list. Never commit `.env.local` — `.gitignore` already excludes it.

## Auth flow

`AuthProvider` subscribes to `supabase.auth.onAuthStateChange` and exposes
`{ user, session, loading, signIn, signUp, signInWithProvider, signOut }`.
Pages requiring auth are wrapped with `<ProtectedRoute>`, which redirects
unauthenticated users to `/login` (preserving the original destination via
`location.state.from`).

## Deployment

Three ready-to-go targets — pick one:

- **Vercel** — `vercel.json` is committed; just import the repo and set the
  `VITE_*` env vars in the project settings.
- **Netlify** — `netlify.toml` is committed; same env-var setup applies.
- **Docker / self-hosted** — `Dockerfile` + `nginx.conf` produce a static
  Nginx image with SPA fallback, security headers, and asset caching.

  ```bash
  docker build \
    --build-arg VITE_SUPABASE_URL=https://xxx.supabase.co \
    --build-arg VITE_SUPABASE_ANON_KEY=eyJ... \
    -t podcraft-ai .
  docker run -p 8080:80 podcraft-ai
  ```

GitHub Actions CI lives in `.github/workflows/ci.yml` (type-check, lint, test,
build on every PR). `.github/workflows/deploy.yml` is a template for the
provider you choose.

## Legacy `js/` folder

The `js/` directory contains pre-React static-HTML scripts that are **no longer
wired up**. See `js/DEPRECATED.md` — safe to delete once you've confirmed
nothing external links to it.
