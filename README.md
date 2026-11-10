# 🥔 Potato Chip Store

A demo online store where shoppers build their own bag of chips: pick a base chip, then add 1–3 flavors. It's built as a training project for learning to make a real-world app with Streamlit, Supabase and GitHub.

> **Status:** Planning complete. No application code yet; the foundation (F1–F15) is next.
> **Demo only:** No real payments, no real emails, fictional data.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| App | [Streamlit](https://streamlit.io) (Python 3.11+) | Storefront, cart, checkout and admin screens |
| Backend | [Supabase](https://supabase.com) | Postgres database, sign-in, product image storage |
| Hosting | [Streamlit Community Cloud](https://streamlit.io/cloud) | Recommended; see [ADR 0001](docs/architecture/decisions/0001-hosting-platform.md) |
| Collaboration | GitHub | Issues, pull requests, Actions (CI) |

## Start Here

1. [docs/requirements/00-consolidated-requirements.md](docs/requirements/00-consolidated-requirements.md): what we're building
2. [docs/planning/work-division-plan.md](docs/planning/work-division-plan.md): who builds what, and how we use GitHub

## Repository Structure

```
potato-chip-store/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Project context and rules for Claude Code
├── requirements.txt           ← Python packages
├── skills-lock.json           ← Agent skills installed with `npx skills add`
├── .env.example               ← Copy to .env (never commit .env)
├── .gitignore
│
├── .streamlit/
│   ├── config.toml            ← Theme and settings
│   └── secrets.toml.example   ← Copy to secrets.toml (never commit it)
│
├── .claude/
│   ├── skills/                ← Agent skills (Streamlit, Supabase, UI/UX)
│   └── hooks/                 ← Docs for automated checks
│
├── app/                       ← Streamlit application
│   ├── pages/                 ← One file per screen (S1–S16)
│   ├── components/            ← Reusable UI pieces (product card, flavor tile…)
│   ├── services/              ← All Supabase calls (catalog, cart, orders, admin, auth)
│   ├── models/                ← Data classes (BaseChip, Flavor, Bag, Order…)
│   ├── utils/                 ← Helpers (pricing, guards, session, outbox)
│   └── config/                ← Loads settings and secrets
│
├── assets/
│   ├── images/                ← Logos and product images
│   └── styles/                ← Custom CSS (keep it small)
│
├── docs/
│   ├── requirements/          ← 00 summary, 01 stories, 02 UI/UX, 03 non-functional
│   ├── planning/              ← Work division plan, personas, story map, backlog
│   ├── architecture/          ← Architecture, data model, ADRs (decisions/)
│   ├── deployment/            ← How to deploy (Streamlit Community Cloud)
│   └── design/                ← Wireframes and mockups
│
├── supabase/
│   ├── migrations/            ← SQL schema migrations (RLS on every table)
│   └── seed/                  ← Demo data
│
├── tests/
│   ├── unit/                  ← Fast tests, no database
│   └── integration/           ← Tests against a local Supabase
│
└── scripts/                   ← Helper scripts (seed users, create issues…)
```

Empty folders contain a `.gitkeep` file so Git keeps them.

## Getting Started

Full setup steps are added in foundation item F15. In short:

1. Install Python 3.11+, Git, Node.js, the GitHub CLI, Docker and the Supabase CLI.
2. Clone the repo, then create a virtual environment: `python -m venv .venv`.
3. Install the packages: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, then fill in your Supabase values.
5. Run the app: `streamlit run app/main.py`.
