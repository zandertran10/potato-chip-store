# 0001: Hosting Platform

- **Status:** Proposed (open)
- **Date:**

## Context
The planned stack is Streamlit + Supabase, hosted on Vercel.

Streamlit runs as a long-lived Python server that talks to the browser over websockets. Vercel is designed for static sites and short-lived serverless functions, so a Streamlit app does not run reliably there without workarounds.

## Options
1. **Vercel**: the original plan; needs research to confirm Streamlit can run there.
2. **Streamlit Community Cloud**: built for Streamlit, simple to set up.
3. **Render / Railway / Fly.io**: run Streamlit as a normal web server.
4. **Vercel for a marketing site + another host for the Streamlit store.**

## Decision
**Recommended: Streamlit Community Cloud** (option 2). The Lead confirms this and changes the status to Accepted in foundation item F6.

Why: it's built for Streamlit, free, deploys straight from GitHub, keeps keys in its Secrets settings, and is the target used by the training playbook.

## Consequences
- The app's entry point is `app/main.py`. Staging deploys from `main`, and production deploys from release tags (see `docs/deployment/`).
- Files written on the server, such as the `outbox/` folder, are temporary and cleared when the app restarts. That's acceptable for a demo.
- Free-tier limits apply: the app sleeps when it isn't being used, and resources are limited.
- Vercel is no longer the hosting plan. It could still be used later for a separate marketing site (option 4).
