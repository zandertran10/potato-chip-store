# Deployment

The full steps are written in foundation item **F15**. This page is the outline.

## Environments

| Environment | Supabase | App | Deployed from |
|-------------|----------|-----|---------------|
| Local | `supabase start` (Docker) | `streamlit run app/main.py` | Your branch |
| Staging | Shared staging project | Streamlit Community Cloud | `main` |
| Production | Separate production project | Streamlit Community Cloud | Release tags (`v1.0.0`) |

## Streamlit Community Cloud (outline)

1. Sign in at share.streamlit.io with GitHub.
2. **Create app:** choose the repo and branch, and set the main file to `app/main.py`.
3. **Advanced settings:** Python 3.11+. In **Secrets**, paste the same keys as in `.streamlit/secrets.toml.example`, filled in. They are never committed.
4. Deploy, then run the smoke test: open the home page, sign in, place an order, open the admin pages.

## Notes
- Apply database migrations to staging before production.
- The `outbox/` folder on Streamlit Community Cloud is temporary and cleared when the app restarts. That's accepted for the demo (NFR-DEP-07).
- Rollback: redeploy the previous tag.
