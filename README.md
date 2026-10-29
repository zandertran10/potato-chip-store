# 🥔 Potato Chip Store

An online store for selling potato chips.

> **Status:** Project setup only. No application code has been written yet. This repo currently holds the folder structure and planning documents.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend / App | [Streamlit](https://streamlit.io) (Python) | Storefront UI, product pages, cart, checkout |
| Backend | [Supabase](https://supabase.com) | Postgres database, authentication, storage for product images |
| Hosting | [Vercel](https://vercel.com) | Deployment of the web app (see the hosting note below) |

## Repository Structure

```
potato-chip-store/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Project context and rules for Claude (AI assistant)
├── .gitignore
│
├── .claude/                   ← Claude configuration
│   ├── skills/                ← Reusable instruction sets for Claude
│   │   ├── README.md
│   │   └── _template/SKILL.md ← Copy this to create a new skill
│   └── hooks/                 ← Docs for automated checks Claude runs
│       └── README.md
│
├── docs/                      ← All planning and design documentation
│   ├── story-mapping/         ← Personas, user journey, story map, backlog
│   │   ├── README.md
│   │   ├── personas.md
│   │   ├── story-map.md
│   │   └── backlog.md
│   └── design/                ← Architecture, data model, UI/UX
│       ├── README.md
│       ├── architecture.md
│       ├── data-model.md
│       ├── ui-ux.md
│       ├── wireframes/        ← Sketches and mockup images
│       └── decisions/         ← Architecture Decision Records (ADRs)
│           ├── README.md
│           └── 0001-hosting-platform.md
│
├── app/                       ← Streamlit application (empty for now)
│   ├── pages/                 ← Streamlit multipage screens (Shop, Cart, Checkout…)
│   ├── components/            ← Reusable UI pieces (product card, header…)
│   ├── services/              ← Supabase data access (products, orders, auth)
│   └── utils/                 ← Helpers (formatting, validation)
│
├── supabase/                  ← Database work (empty for now)
│   ├── migrations/            ← SQL schema migrations
│   └── seed/                  ← Sample data (sample chip flavors, etc.)
│
├── assets/images/             ← Logos, product photos, brand assets
└── tests/                     ← Automated tests (empty for now)
```

Empty folders contain a `.gitkeep` file so Git keeps them in the repository.

## Suggested Workflow

1. **Plan:** fill in `docs/story-mapping/` (who buys chips, what they need to do).
2. **Design:** fill in `docs/design/` (architecture, tables, screens), and record big choices in `docs/design/decisions/`.
3. **Build:** write code in `app/` and `supabase/` only after the plan and design are agreed.
4. **Test and deploy.**

## Hosting Note

Streamlit runs as a long-lived server using websockets, and Vercel is built mainly for static sites and short-lived serverless functions, so Streamlit does not run well on Vercel out of the box. This is tracked as an open decision in [`docs/design/decisions/0001-hosting-platform.md`](docs/design/decisions/0001-hosting-platform.md).

## Getting Started

Setup instructions will be added once the first code is written.
