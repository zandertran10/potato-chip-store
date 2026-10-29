# CLAUDE.md: Project Context for Claude

This file gives Claude (AI coding assistant) the context it needs when working in this repo.

## Project
An online store that sells potato chips.

## Tech Stack
- **App:** Streamlit (Python)
- **Backend:** Supabase (Postgres, Auth, Storage)
- **Hosting:** Vercel (see `docs/design/decisions/0001-hosting-platform.md`)

## Where Things Live
- Planning: `docs/story-mapping/`
- Design: `docs/design/`
- App code: `app/`
- Database: `supabase/`
- Claude skills: `.claude/skills/`
- Claude hooks: `.claude/hooks/`

## Rules for Claude
- Read the relevant docs in `docs/` before writing code.
- Never commit secrets. Supabase keys go in environment variables, never in code.
- Enable Row Level Security (RLS) on every Supabase table.
- Keep changes small and explain them.
- Record any major technical choice as a new ADR in `docs/design/decisions/`.
