# CLAUDE.md: Project Context for Claude

This file gives Claude (AI coding assistant) the context it needs when working in this repo.

## Project
A demo online store that sells potato chips. Shoppers build their own bag: one base chip plus 1–3 flavor add-ons. It's built for training: no real payments, no real emails, fictional data, age-appropriate content.

## Tech Stack
- **App:** Streamlit (Python 3.11+, Streamlit 1.57+)
- **Backend:** Supabase (Postgres, Auth, Storage)
- **Hosting:** Streamlit Community Cloud (recommended; see `docs/architecture/decisions/0001-hosting-platform.md`)
- **Collaboration:** GitHub (issues, PRs, Actions)

## Where Things Live
- Requirements: `docs/requirements/` (start with `00-consolidated-requirements.md`; the data model is in section 6)
- Work plan: `docs/planning/work-division-plan.md` (pick codes, file ownership, GitHub workflow)
- Architecture and ADRs: `docs/architecture/`
- Deployment: `docs/deployment/`
- UI design and wireframes: `docs/design/`
- App code: `app/` (`pages`, `components`, `services`, `models`, `utils`, `config`)
- Database: `supabase/` (`migrations`, `seed`)
- Tests: `tests/unit/`, `tests/integration/`
- Scripts: `scripts/`
- Claude skills: `.claude/skills/` · Claude hooks: `.claude/hooks/`

## Rules for Claude
- Read the relevant docs in `docs/` before writing code.
- Never commit secrets. Supabase keys go in `.env` or `.streamlit/secrets.toml` (both gitignored), never in code.
- Enable Row Level Security (RLS) on every Supabase table.
- Pages never call Supabase directly; use `app/services/`.
- One story = one branch = one PR = one squash commit (see the work plan, section 2).
- Keep changes small and explain them.
- Record any major technical choice as a new ADR in `docs/architecture/decisions/`.
