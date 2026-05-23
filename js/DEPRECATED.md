# ⚠️ DEPRECATED — `js/` directory

The plain-JS files in this folder (`auth.js`, `dashboard.js`, `personas.js`,
`audio-agent.js`, `supabase-config.js`) belong to an earlier static-HTML version of
PodCraft AI. The application is now a React SPA powered by Vite + React Router,
and **none of these scripts are loaded by the current `index.html`**.

## What replaced them

| Legacy file              | Replacement in the React app                                        |
| ------------------------ | ------------------------------------------------------------------- |
| `supabase-config.js`     | `src/lib/supabase.ts` (env-driven client)                           |
| `auth.js`                | `src/app/providers/auth-provider.tsx` + `useAuth()` hook            |
| `auth.js` (UI bindings)  | `src/app/pages/login-page.tsx`, `src/app/pages/sign-up-page.tsx`    |
| Protected-page redirects | `src/app/components/protected-route.tsx`                            |
| Toast notifications      | `sonner` `<Toaster />` mounted in `src/main.tsx`                    |

## Why it can't just stay

- It hardcodes the Supabase URL + anon key in committed source code.
- It targets DOM IDs from HTML files (`signin.html`, `dashboard.html`, …) that
  don't exist in the SPA, so it would silently no-op even if loaded.
- It duplicates auth logic that the React `AuthProvider` already owns, and the
  two implementations can drift out of sync.

## Action

This folder is excluded from TypeScript (`tsconfig.json`), ESLint, and Prettier.
It's also excluded from the Docker build (`.dockerignore`). When you've confirmed
nothing else references it, delete the entire `js/` directory:

```bash
git rm -r js
```
