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
To be decided.

## Consequences
To be filled in after the decision.
